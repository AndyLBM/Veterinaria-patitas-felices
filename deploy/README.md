# Integración local con Apache/XAMPP

Estado: configuración propuesta; no se ha modificado ni reiniciado Apache.
En la instalación inspeccionada `mod_proxy` está activo, `mod_proxy_http`
está comentado y no hay un proxy `/api/` configurado.
El ejemplo se validó con `httpd.exe -t`, cargando el módulo y el Include solo
para esa comprobación: resultado `Syntax OK`. No sustituye su activación manual
ni una prueba HTTP a través de Apache.

1. Respaldar manualmente `C:/xampp/apache/conf/httpd.conf`.
2. Activar `LoadModule proxy_http_module modules/mod_proxy_http.so`.
3. Añadir, fuera de bloques Directory y después de cargar los módulos:

   ```apache
   Include "C:/Users/User/Documents/Patitas Felices/deploy/apache-api.conf.example"
   ```

4. Validar con `C:/xampp/apache/bin/httpd.exe -t` y reiniciar Apache desde XAMPP
   solo si la validación es correcta.
5. Desde la raíz del proyecto instalar requirements y arrancar FastAPI:

   ```powershell
   & .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   & .\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --root-path /api --proxy-headers --forwarded-allow-ips 127.0.0.1
   ```

6. Verificar `http://localhost/api/`, `/api/openapi.json` y `/api/docs`.
   `/api/auth/me` sin token debe responder 401. Usar las barras finales que
   declara OpenAPI; `root-path` conserva `/api` en documentación y redirecciones.

El frontend se servirá desde Apache, con su DocumentRoot limitado a
archivos públicos. Nunca publicar la raíz del repositorio: contiene `.env`.
Consumirá URLs como `/api/auth/login` y `/api/citas/mi-agenda` mediante Fetch
y Authorization Bearer. El proxy conserva Authorization. No se necesita CORS
al compartir origen; no se han añadido comodines ni excepciones CORS.
El ejemplo restringe `/api/` a conexiones locales y FastAPI escucha solo loopback.
No usar `ProxyRequests On` ni ejecutar FastAPI con acceso público para esta prueba.

## Contrato de fechas y disponibilidad

- Referencia: `America/Lima`. tzdata proporciona la zona IANA también en Windows.
- MySQL mantiene sus DATETIME originales: no hay migración ni actualización.
- Fechas sin offset se interpretan como hora civil de Lima. Fechas de entrada
  con offset se convierten a Lima antes de validarse/guardarse. Por ejemplo,
  `15:00Z`, `10:00-05:00` y `10:00` representan la misma hora de negocio.
- Las respuestas existentes de fechas conservan el formato local sin offset.
  El frontend no debe reinterpretarlas como UTC ni añadir `Z`.
- GET de horarios devuelve `hora_inicio` y `hora_fin` como `HH:mm:ss`, en vez de
  segundos. Los repositories y cálculos internos conservan TIME/timedelta.
- Para nuevas reservas: `GET /citas/disponibilidad` con servicio, veterinario y
  fecha. Para reprogramar: `GET /citas/{id_cita}/disponibilidad-reprogramacion`
  con `id_veterinario` destino y `fecha` (YYYY-MM-DD). El backend obtiene duración,
  servicio y mascota de la cita, excluye esa cita y considera ocupaciones tanto
  de la mascota como del veterinario. Solo administrador o cliente propietario.
- La consulta de disponibilidad es orientativa: PATCH reprogramacion revalida
  horarios, propiedad, plazo, estado y solapamientos bajo transacción y bloqueos.
- `GET /citas/mi-agenda`: solo veterinario activo; filtros fecha_desde,
  fecha_hasta y estado. Un id_veterinario enviado no selecciona otra agenda.
- `GET /citas/{id_cita}` admite veterinario asignado, además de los permisos
  existentes. `GET /citas/{id_cita}/atencion`: administrador o veterinario
  asignado, 404 si no hay atención; nunca crea registros. Cliente sigue denegado.

Referencias: [Apache mod_proxy](https://httpd.apache.org/docs/2.4/mod/mod_proxy.html),
[FastAPI detrás de proxy](https://fastapi.tiangolo.com/advanced/behind-a-proxy/),
[Python zoneinfo](https://docs.python.org/3/library/zoneinfo.html).
