using System;
using System.ComponentModel;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Speech.Synthesis;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Threading;
using Microsoft.Kinect;
using Microsoft.Win32;

namespace LSCKinectFramework
{
    public partial class MainWindow : Window
    {
        private KinectSensor sensor;
        private SpeechSynthesizer voz;

        private bool deletreando;
        private volatile bool cerrando;
        private bool cierreCompleto;

        private int procesando;
        private DateTime siguienteFrame = DateTime.MinValue;

        // El texto se conserva separado de los mensajes de estado.
        private string textoGenerado = "";

        private readonly SemaphoreSlim accesoEstado =
            new SemaphoreSlim(1, 1);

        private readonly DispatcherTimer temporizador =
            new DispatcherTimer
            {
                Interval = TimeSpan.FromMilliseconds(500)
            };

        private readonly HttpClient detector =
            new HttpClient(
                new HttpClientHandler
                {
                    UseProxy = false
                })
            {
                BaseAddress =
                    new Uri("http://127.0.0.1:8765/"),

                Timeout = TimeSpan.FromSeconds(3)
            };

        public MainWindow()
        {
            InitializeComponent();

            Loaded += VentanaCargada;
            Closing += VentanaCerrando;
            temporizador.Tick += ConsultarDeletreo;
        }

        private async void VentanaCargada(
            object sender,
            RoutedEventArgs e)
        {
            try
            {
                sensor = KinectSensor.KinectSensors
                    .FirstOrDefault(
                        k => k.Status == KinectStatus.Connected);

                if (sensor == null)
                {
                    EstadoKinect.Text =
                        "No se encontró un Kinect conectado.";
                    return;
                }

                sensor.ColorStream.Enable(
                    ColorImageFormat.RgbResolution640x480Fps30);

                sensor.ColorFrameReady += Sensor_ColorFrameReady;
                sensor.Start();

                EstadoKinect.Text = "Kinect conectado.";

                await accesoEstado.WaitAsync();

                try
                {
                    await ActualizarTextoDeletreo();
                }
                finally
                {
                    accesoEstado.Release();
                }
            }
            catch (Exception ex)
            {
                if (!cerrando)
                    EstadoDeletreo.Text = ex.Message;
            }
        }

        private async void Sensor_ColorFrameReady(
            object sender,
            ColorImageFrameReadyEventArgs e)
        {
            if (cerrando ||
                Interlocked.CompareExchange(
                    ref procesando, 1, 0) != 0)
            {
                return;
            }

            try
            {
                byte[] pixels;
                int ancho;
                int alto;

                using (ColorImageFrame frame =
                    e.OpenColorImageFrame())
                {
                    if (frame == null ||
                        DateTime.UtcNow < siguienteFrame)
                    {
                        return;
                    }

                    ancho = frame.Width;
                    alto = frame.Height;

                    pixels = new byte[frame.PixelDataLength];
                    frame.CopyPixelDataTo(pixels);
                }

                siguienteFrame =
                    DateTime.UtcNow.AddMilliseconds(50);

                BitmapSource original = BitmapSource.Create(
                    ancho,
                    alto,
                    96,
                    96,
                    PixelFormats.Bgr32,
                    null,
                    pixels,
                    ancho * 4);

                original.Freeze();

                BitmapSource resultado = original;
                string estado;

                try
                {
                    byte[] jpeg = await Task.Run(
                        () => ConvertirAJpeg(original));

                    using (var contenido =
                        new ByteArrayContent(jpeg))
                    {
                        contenido.Headers.ContentType =
                            new System.Net.Http.Headers
                                .MediaTypeHeaderValue("image/jpeg");

                        using (var respuesta =
                            await detector.PostAsync(
                                "detect",
                                contenido))
                        {
                            respuesta.EnsureSuccessStatusCode();

                            byte[] imagenProcesada =
                                await respuesta.Content
                                    .ReadAsByteArrayAsync();

                            resultado =
                                CrearImagen(imagenProcesada);

                            string cantidad =
                                respuesta.Headers
                                    .GetValues("X-Hands-Count")
                                    .First();

                            estado =
                                "Manos detectadas: " + cantidad +
                                " | Cámara conectada";
                        }
                    }
                }
                catch (Exception ex)
                {
                    estado =
                        "Cámara activa. Detector no disponible: " +
                        ex.Message;
                }

                if (!cerrando)
                {
                    await Dispatcher.InvokeAsync(() =>
                    {
                        if (cerrando)
                            return;

                        ImagenKinect.Source = resultado;
                        EstadoKinect.Text = estado;
                    });
                }
            }
            catch (Exception ex)
            {
                if (!cerrando)
                {
                    await Dispatcher.InvokeAsync(() =>
                    {
                        if (!cerrando)
                        {
                            EstadoKinect.Text =
                                "Error de imagen: " + ex.Message;
                        }
                    });
                }
            }
            finally
            {
                Interlocked.Exchange(ref procesando, 0);
            }
        }

        private static byte[] ConvertirAJpeg(
            BitmapSource imagen)
        {
            var encoder = new JpegBitmapEncoder
            {
                QualityLevel = 85
            };

            encoder.Frames.Add(
                BitmapFrame.Create(imagen));

            using (var stream = new MemoryStream())
            {
                encoder.Save(stream);
                return stream.ToArray();
            }
        }

        private static BitmapSource CrearImagen(
            byte[] datos)
        {
            using (var stream = new MemoryStream(datos))
            {
                var bitmap = new BitmapImage();

                bitmap.BeginInit();
                bitmap.CacheOption =
                    BitmapCacheOption.OnLoad;
                bitmap.StreamSource = stream;
                bitmap.EndInit();

                bitmap.Freeze();
                return bitmap;
            }
        }

        private async Task EnviarComando(string comando)
        {
            using (var contenido = new StringContent(""))
            using (var respuesta = await detector.PostAsync(
                "spell/" + comando,
                contenido))
            {
                if (!respuesta.IsSuccessStatusCode)
                {
                    string detalle =
                        await respuesta.Content
                            .ReadAsStringAsync();

                    throw new Exception(detalle);
                }
            }
        }

        private async Task ActualizarTextoDeletreo()
        {
            using (var respuesta =
                await detector.GetAsync("spell/status"))
            {
                respuesta.EnsureSuccessStatusCode();

                string mensaje =
                    (await respuesta.Content.ReadAsStringAsync())
                    .Replace("\r\n", "\n");

                const string prefijo = "Texto: ";

                int separador = mensaje.IndexOf(
                    "\nEstado:",
                    StringComparison.Ordinal);

                if (!mensaje.StartsWith(
                        prefijo,
                        StringComparison.Ordinal) ||
                    separador < prefijo.Length)
                {
                    throw new Exception(
                        "El servidor devolvió un estado no válido.");
                }

                string texto = mensaje.Substring(
                    prefijo.Length,
                    separador - prefijo.Length);

                string estado = mensaje.Substring(
                    separador + "\nEstado:".Length).Trim();

                if (cerrando)
                    return;

                textoGenerado = texto == "—" ? "" : texto;

                if (TextoDeletreo.Text != textoGenerado)
                {
                    TextoDeletreo.Text = textoGenerado;
                    TextoDeletreo.ScrollToEnd();
                }

                ContadorTexto.Text =
                    textoGenerado.Length + " caracteres";

                EstadoDeletreo.Text = estado;
            }
        }

        private async void ConsultarDeletreo(
            object sender,
            EventArgs e)
        {
            if (cerrando ||
                !await accesoEstado.WaitAsync(0))
            {
                return;
            }

            try
            {
                await ActualizarTextoDeletreo();
            }
            catch (Exception ex)
            {
                if (!cerrando)
                {
                    EstadoDeletreo.Text =
                        "Sin respuesta del detector: " +
                        ex.Message;
                }
            }
            finally
            {
                accesoEstado.Release();
            }
        }

        private async void Deletreo_Click(
            object sender,
            RoutedEventArgs e)
        {
            if (cerrando)
                return;

            if (!deletreando &&
                (sensor == null || !sensor.IsRunning))
            {
                EstadoDeletreo.Text =
                    "Conecta el Kinect antes de iniciar.";
                return;
            }

            BotonDeletreo.IsEnabled = false;

            await accesoEstado.WaitAsync();

            try
            {
                if (cerrando)
                    return;

                await EnviarComando(
                    deletreando ? "stop" : "start");

                if (cerrando)
                    return;

                deletreando = !deletreando;

                BotonDeletreo.Content =
                    deletreando
                        ? "Detener deletreo"
                        : "Iniciar deletreo";

                BotonDeletreo.Background =
                    (Brush)new BrushConverter()
                        .ConvertFromString(
                            deletreando
                                ? "#9F1239"
                                : "#12634B");

                ModoDeletreo.Text =
                    deletreando
                        ? "DELETREO ACTIVO"
                        : "EN PAUSA";

                if (deletreando)
                    temporizador.Start();
                else
                    temporizador.Stop();

                await ActualizarTextoDeletreo();
            }
            catch (Exception ex)
            {
                if (!cerrando)
                {
                    EstadoDeletreo.Text =
                        "No se pudo cambiar el modo: " +
                        ex.Message;
                }
            }
            finally
            {
                accesoEstado.Release();

                if (!cerrando)
                    BotonDeletreo.IsEnabled = true;
            }
        }

        private async void EditarTexto_Click(
            object sender,
            RoutedEventArgs e)
        {
            if (cerrando)
                return;

            var boton = sender as Button;

            if (boton == null)
                return;

            EdicionTexto.IsEnabled = false;

            await accesoEstado.WaitAsync();

            try
            {
                if (cerrando)
                    return;

                await EnviarComando(
                    boton.Tag.ToString());

                await ActualizarTextoDeletreo();
            }
            catch (Exception ex)
            {
                if (!cerrando)
                {
                    EstadoDeletreo.Text =
                        "No se pudo editar: " + ex.Message;
                }
            }
            finally
            {
                accesoEstado.Release();

                if (!cerrando)
                    EdicionTexto.IsEnabled = true;
            }
        }

        private void GuardarTexto_Click(
            object sender,
            RoutedEventArgs e)
        {
            if (string.IsNullOrWhiteSpace(textoGenerado))
            {
                EstadoDeletreo.Text =
                    "Todavía no hay texto para guardar.";
                return;
            }

            // Conservar una copia del texto al pulsar el botón.
            string copia = textoGenerado;

            var ventana = new SaveFileDialog
            {
                Title = "Guardar texto reconocido",
                Filter = "Archivo de texto (*.txt)|*.txt",
                FileName = "texto_lsc.txt",
                DefaultExt = ".txt",
                AddExtension = true
            };

            if (ventana.ShowDialog(this) != true)
                return;

            try
            {
                File.WriteAllText(
                    ventana.FileName,
                    copia,
                    new UTF8Encoding(false));

                EstadoDeletreo.Text =
                    "Texto guardado correctamente.";
            }
            catch (Exception ex)
            {
                EstadoDeletreo.Text =
                    "No se pudo guardar: " + ex.Message;
            }
        }

        private void LeerTexto_Click(
            object sender,
            RoutedEventArgs e)
        {
            if (string.IsNullOrWhiteSpace(textoGenerado))
            {
                EstadoDeletreo.Text =
                    "Todavía no hay texto para leer.";
                return;
            }

            try
            {
                if (voz == null)
                {
                    voz = new SpeechSynthesizer();
                    voz.SetOutputToDefaultAudioDevice();
                }

                var espanola = voz.GetInstalledVoices()
                    .FirstOrDefault(v =>
                        v.Enabled &&
                        v.VoiceInfo.Culture
                            .TwoLetterISOLanguageName == "es");

                if (espanola == null)
                {
                    EstadoDeletreo.Text =
                        "Instala una voz en español " +
                        "compatible con System.Speech.";
                    return;
                }

                voz.SpeakAsyncCancelAll();
                voz.SelectVoice(espanola.VoiceInfo.Name);

                voz.Rate = 0;
                voz.Volume = 100;

                voz.SpeakAsync(textoGenerado);
            }
            catch (Exception ex)
            {
                EstadoDeletreo.Text =
                    "No se pudo leer el texto: " +
                    ex.Message;
            }
        }

        private async void VentanaCerrando(
            object sender,
            CancelEventArgs e)
        {
            if (cierreCompleto)
                return;

            e.Cancel = true;

            if (cerrando)
                return;

            cerrando = true;
            temporizador.Stop();
            IsEnabled = false;

            if (sensor != null)
            {
                sensor.ColorFrameReady -=
                    Sensor_ColorFrameReady;

                try
                {
                    sensor.Stop();
                }
                catch
                {
                    // El sensor puede estar desconectado.
                }
            }

            try
            {
                if (voz != null)
                {
                    voz.SpeakAsyncCancelAll();
                    voz.Dispose();
                }
            }
            catch
            {
                // Continuar cerrando la aplicación.
            }

            detector.CancelPendingRequests();

            // Detener el deletreo sin cerrar Python.
            try
            {
                await EnviarComando("stop");
            }
            catch
            {
                // El servidor puede estar apagado.
            }

            detector.Dispose();

            cierreCompleto = true;
            Close();
        }
    }
}
