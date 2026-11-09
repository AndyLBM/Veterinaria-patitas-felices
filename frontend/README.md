# Frontend · Fase 17: evaluación de calidad y seguridad

Integración general verificada en la Fase 16; resultados y límites en
`deploy/phase16-summary.md`.

HTML5, CSS3 y módulos ES sin dependencias de ejecución ni compilación.
Login y registro de clientes conectados a los contratos de FastAPI mediante Fetch.
Incluye panel administrativo, usuarios, clientes, veterinarios, especialidades y servicios.
Incluye también horarios semanales y supervisión administrativa de citas.
El cliente dispone de panel, mascotas propias y perfil de lectura.
Incluye reserva, mis citas, cancelación y reprogramación de fecha/hora con el veterinario actual.
No hay usuarios de muestra ni JWT precargados.
El formulario de la galería solo demuestra validación local: no guarda ni envía datos.
La navegación privada se bloquea antes de cargar la vista y el backend conserva
la responsabilidad de autorizar cada operación. El veterinario dispone de agenda y atención clínica.

## Visualización mediante Apache/XAMPP

La configuración aprobada ya está activa en `C:/xamppCalidad`. No es necesario
volver a añadir Include ni modificar Apache para esta fase. Los detalles están
en `deploy/phase10_1-results.md` y `deploy/phase11_1-results.md`.
Abrir `http://localhost/patitas/` con Apache, FastAPI y MySQL en funcionamiento.
El Alias publica solo frontend/ y restringe el acceso a conexiones locales.
No publicar la raíz del proyecto ni modificar la instalación `C:/xampp`.

Comprobar `http://localhost/api/` (JSON de estado) y `/api/auth/me` (401 sin token).
La interfaz usa el meta `api-base` de index.html, por defecto `/api/`.
No se necesita CORS al compartir origen. Un origen distinto requiere configurar
el backend expresamente; no se debe sortear CORS con `no-cors`.

## Visualización estática independiente

Desde la raíz, para revisar la interfaz sin modificar Apache:

```powershell
& .\.venv\Scripts\python.exe -m http.server 5510 --bind 127.0.0.1 --directory frontend
```

Abrir `http://127.0.0.1:5510/#/acceso`. En este servidor `/api/` no tiene proxy: la pantalla
de conexión mostrará un error si se pulsa Comprobar. La interfaz no llama a la
API al abrirse. No usar file://, porque las vistas y módulos se sirven por HTTP.

## Arquitectura

- `views/`: plantillas HTML locales; ninguna ruta se construye con HTML del usuario.
- `js/core/`: HTTP, errores, sesión en memoria, catálogo de rutas y permisos.
- `js/components/`: navegación, botones, campos, tablas, diálogos, estados y avisos.
- `js/pages/`: comportamiento de cada vista; `js/api/`: rutas de API.
- `js/adapters/`: formatos de datos. Las fechas civiles de Lima no se convierten a UTC.
- `assets/css/`: tokens, base, layout, componentes, vistas y contraste accesible; `assets/img/`: SVG locales.

El cliente HTTP central permite get/post/put/patch con JSON. `auth:false` omite
Bearer. El login usa un token candidato para consultar `/auth/me` antes de
invocar setVerifiedSession. El rol confirmado por `/auth/me` decide el destino.
No hay persistencia del token: al recargar se pierde la sesión. Un 401 protegido
limpia la sesión; un 403 no la cierra. No se reintentan escrituras automáticamente.
Solicitudes idénticas pendientes se rechazan con DUPLICATE_REQUEST. Las vistas
reciben un AbortSignal que se cancela al navegar. Un cierre de sesión cancela
solicitudes pendientes y evita que un login tardío reinstale la sesión.

## Uso del acceso y registro

- Login: `#/acceso`. POST `/api/auth/login` y GET `/api/auth/me`.
- Registro: `#/registro`. POST `/api/clientes/registro`, sin parámetro de rol.
- El registro confirma la creación y ofrece ir al login; no inicia sesión.
- Destinos: `#/admin/panel`, `#/veterinario/panel`, `#/cliente/panel`.
- Cerrar sesión es local: borra el token, retira la vista privada y vuelve al login.
- La expiración del JWT se usa solo como ayuda de interfaz, después de verificar
  la identidad con el servidor. El backend sigue comprobando firma, estado y rol.
- Al recargar no se restaura ningún token. No hay refresh ni revocación.
- Contraseñas: registro mínimo 8 caracteres, login mínimo 1; ambos máximo
  72 caracteres y 72 bytes UTF-8, según el backend/bcrypt. No se recortan espacios
  de la contraseña. Nombre/apellido: 2–80; correo: 5–150; teléfono opcional: 20.
- Errores 401 del login se muestran como credenciales incorrectas. Un 401 de
  `/auth/me` candidato no instala sesión. Un 401 protegido limpia la sesión
  vigente; un 403 la conserva. Los errores 422 se asocian al campo correspondiente.

La integración HTTP real está validada con Apache de `C:/xamppCalidad`,
Alias `/patitas/`, proxy `/api/`, FastAPI y MySQL. No se habilitó CORS.
Para probar con el backend, abrir `http://localhost/patitas/#/registro`, crear
una cuenta autorizada y luego usar `#/acceso`. No usar cuentas ajenas.

## Comprobaciones reproducibles

Con Node 24 y sin instalar paquetes:

```powershell
node --test frontend/tests/*.test.js
node frontend/tests/run-browser.mjs
```

Con el servidor estático abierto, visitar `/tests/browser.html` para ejecutar
las pruebas DOM en el navegador. Son pruebas técnicas locales; no acceden a
MySQL ni crean identidades. La comprobación manual de teclado y el aspecto
visual complementan el informe de esa página.

El ejecutable run-browser.mjs requiere Edge o Brave instalado en Windows. Usa
un perfil temporal propio y su depuración en loopback; lo cierra y elimina al
terminar. Comprueba además Enter, Escape y Tab con eventos reales de teclado
del navegador. Genera resultados JSON y capturas en `tests/artifacts/`.

Las pruebas de autenticación de `auth.test.js` y `auth-browser.js` son simuladas.
La prueba de navegador intercepta Fetch únicamente en su iframe y genera los
valores de ensayo en memoria. No imprime ni guarda contraseñas o candidatos
de token y no contacta FastAPI/MySQL. Esto no aprueba la integración Apache/API.
Los resultados distinguen el navegador real del transporte HTTP simulado.

## Administración

Acceder con una cuenta administrativa autorizada en
`http://localhost/patitas/#/acceso`. El destino es `#/admin/panel`.
Las pantallas administrativas requieren rol 1. Usuarios permite consultar
y cambiar estado; clientes, veterinarios, especialidades y servicios permiten
registrar y editar según sus contratos existentes. Clientes muestra únicamente
cuentas activas; reactivar desde Usuarios. No hay edición de roles, cambio de
contraseñas ni eliminación física desde estas interfaces.

Los filtros son locales sobre el listado completo. Las tablas permiten
desplazamiento horizontal y foco por teclado en pantallas estrechas.
Las ediciones y los cambios de estado requieren confirmación. Los avisos de
administración mantienen el resultado más reciente, sin acumular mensajes.

Horarios (`#/admin/horarios`) permite listar por veterinario, registrar y editar
intervalos semanales, con lunes=1 y domingo=7. El backend no ofrece estado,
eliminación ni transferencia de un horario a otro veterinario.
Citas (`#/admin/citas`) permite filtrar por fechas, estado, veterinario y cliente,
consultar el detalle y solicitar transiciones autorizadas. El cierre a ATENDIDA
sigue exigiendo atención, triaje y consulta en FastAPI.

El panel cuenta los clientes, veterinarios y servicios activos y muestra hasta
cinco próximas citas PROGRAMADA/CONFIRMADA, con hora de Lima. Actualizar panel
vuelve a consultar las fuentes. Los filtros de citas se aplican en FastAPI;
los selectores se completan con las personas presentes en las citas consultadas,
incluidas cuentas inactivas que conservan citas históricas.

La Fase 11.2 tiene su informe en `deploy/phase11_2-results.md`. Sus pruebas reales
se ejecutan de forma explícita, con datos ficticios nuevos y limpieza verificada:

```powershell
& .\.venv\Scripts\python.exe -B -m backend.tests.integration_phase11_2_http --run
```

Requiere la autorización correspondiente para las escrituras de prueba.
Resultados: `backend/tests/reports/phase11_2_http.json` y
`frontend/tests/artifacts/phase11_2-real.json`. Capturas: `agenda-*-desktop.png`
y `agenda-*-mobile.png`. La atención veterinaria se describe en la Fase 14, abajo.

Resultados y endpoints: `deploy/phase11_1-results.md`. Capturas reales:
`frontend/tests/artifacts/admin-*-desktop.png` y `admin-*-mobile.png`.

Para repetir la integración real (crea datos ficticios nuevos y los limpia),
solo con la autorización correspondiente y servicios activos:

```powershell
& .\.venv\Scripts\python.exe -B -m backend.tests.integration_phase11_1_http --run
```

El informe `backend/tests/reports/phase11_1_http.json` registra la línea base,
IDs, relaciones y limpieza. `phase11_1-real.json` contiene los resultados del
navegador real sin interceptar Fetch. La suite `run-browser.mjs` usa respuestas
simuladas y mantiene sus resultados separados.

## Espacio del cliente · Fase 12

Recargar la aplicación e iniciar sesión con una cuenta de cliente autorizada
en `http://localhost/patitas/#/acceso`. Destinos protegidos por rol 3:

- `#/cliente/panel`: bienvenida con los datos reales del login verificado,
  número de mascotas activas, accesos y hasta tres mascotas propias.
- `#/cliente/mascotas`: listar, buscar, registrar, consultar, editar y desactivar.
- `#/cliente/perfil`: nombre, apellido y correo de la última sesión, solo lectura.

El backend obtiene el propietario de la identidad autenticada. El formulario
no ofrece propietario, estado o rol, y sus cuerpos JSON usan una lista cerrada.
Se conserva nombre, especie, raza opcional, sexo contratado, nacimiento opcional
y peso referencial opcional. El contrato no especifica la unidad del peso;
la interfaz no añade una. No se inventan restricciones de fecha de nacimiento.

DELETE `/mascotas/{id}` es una desactivación lógica en el backend. Tras ella,
el listado la omite y el detalle devuelve 404. No existe reactivación en los
contratos actuales y no se ofrece en la interfaz.

El perfil no se puede resolver de forma general: `/auth/me` devuelve id_usuario
e id_rol, pero no id_cliente; GET/PUT `/clientes/{id_cliente}` requieren este
último dato y no hay ruta propia para obtenerlo. No se adivinan IDs, no se usa
el listado administrativo y no se condiciona el perfil a tener mascotas.
Por ello se presenta en lectura el nombre/apellido/correo del login, solo
después de verificar `/auth/me`, conservados en memoria y borrados al salir.
Estos campos de presentación no participan en la autorización.

Las citas del cliente se implementan en la Fase 13 descrita abajo.
El historial de lectura se describe en la Fase 15, abajo. El cliente no dispone
de formularios de escritura clínica.

Informe e inventario: `deploy/phase12-results.md`.
Para repetir las pruebas reales, únicamente con autorización para los datos
ficticios y sus eliminaciones de limpieza:

```powershell
& .\.venv\Scripts\python.exe -B -m backend.tests.integration_phase12_http --run
```

Resultados reales: `backend/tests/reports/phase12_http.json` y
`frontend/tests/artifacts/phase12-real.json`. Capturas: `client-*-desktop.png`
y `client-*-mobile.png`. La suite `run-browser.mjs` usa HTTP simulado.

## Citas del cliente · Fase 13

- `#/cliente/reserva`: mascota propia activa, servicio activo, fecha, consulta
  de veterinarios e intervalos del servidor, selección de hora y resumen antes
  de confirmar. Se vuelve a consultar disponibilidad antes del resumen y el POST
  revalida todo. Ante conflicto, consultar horarios nuevamente.
- `#/cliente/citas`: listado propio, filtros locales por fechas/estado, detalle,
  cancelación y reprogramación. El backend comprueba propiedad, estado y 24 horas.
- Reprogramación: conserva mascota, servicio y duración original. Solo fecha/hora
  con el veterinario actual. El cambio de veterinario queda pendiente por decisión
  del usuario de mantener intacto el backend; ver deploy/phase13-backend-proposal.md.
- Todos los valores de fecha/hora se muestran y envían como hora civil de Lima,
  sin convertirlos a UTC o a la zona del navegador. No se inventan turnos de 15/30
  minutos: se elige una hora dentro de un intervalo devuelto por FastAPI.

El catálogo general no considera la mascota; el POST comprueba su solapamiento.
La disponibilidad específica de reprogramación sí considera mascota y excluye
la propia cita. Mis citas no tiene parámetros de filtro en el backend, por eso
se filtra en memoria únicamente la respuesta del cliente autenticado.

Evidencias: backend/tests/reports/phase13_http.json,
frontend/tests/artifacts/phase13-real.json y deploy/phase13-summary.md.
Prueba real opt-in (requiere autorización para fixtures y su limpieza):

```powershell
& .\.venv\Scripts\python.exe -B -m backend.tests.integration_phase13_http --run
```

No se modificaron backend/app, Apache o MySQL estructuralmente en la Fase 13.

## Atención veterinaria · Fase 14

Iniciar sesión con una cuenta veterinaria autorizada (rol 2) en
`http://localhost/patitas/#/acceso`. El panel `#/veterinario/panel` muestra el
nombre del login verificado y cuenta las citas propias programadas/confirmadas,
en atención y atendidas. Los indicadores abarcan toda la agenda devuelta por
FastAPI; no representan estadísticas de un período seleccionado.

`#/veterinario/agenda`, `#/veterinario/atenciones`, `#/veterinario/recetas` y
`#/veterinario/vacunas` comparten el espacio de trabajo: filtrar por fechas y
estado, abrir una cita asignada y consultar sus registros. La información del
cliente y mascota procede del detalle real de la cita. No se consultan listados
administrativos para resolver sus identidades.

El flujo permite confirmar una cita PROGRAMADA e iniciar una CONFIRMADA.
En EN_ATENCION se registra una atención, un triaje y una consulta, y varias
recetas, medicamentos y vacunas. Los registros existentes se pueden editar,
salvo la atención inicial, cuyo backend no ofrece actualización. Diagnóstico,
medicamento/dosis y nombre/fecha de vacuna son obligatorios en sus formularios.
Las vacunas se registran bajo la consulta, sin enviar un id_atencion arbitrario.

El cierre confirmado a ATENDIDA exige atención, triaje y consulta en FastAPI.
Después, los registros quedan en lectura; las escrituras directas también son
rechazadas por el servidor. Guardar o cancelar el formulario abierto antes de
solicitar un cambio de estado. No existen eliminaciones clínicas en la interfaz.

Se conservan en memoria únicamente nombre, apellido y correo de presentación
para roles 2 y 3, después de verificar /auth/me. No intervienen en la autorización
y se borran al salir, expirar o recargar; el JWT tampoco se persiste.

Pruebas simuladas: `node --test frontend/tests/*.test.js` y
`node frontend/tests/run-browser.mjs`. Integración real, únicamente con
autorización para crear y limpiar fixtures y con los servicios activos:

```powershell
& .\.venv\Scripts\python.exe -B -m backend.tests.integration_phase14_http --run
```

Este comando realiza escrituras de prueba reales, inventaría IDs/relaciones y
limpia exclusivamente los registros propios, comparando las 15 tablas con su
línea base. No ejecutarlo concurrentemente con otras escrituras de ensayo.
Resultados e inventario: `backend/tests/reports/phase14_http.json`;
navegador real: `tests/artifacts/phase14-real.json`. Capturas reales:
`tests/artifacts/vet-*-desktop.png` y `vet-*-mobile.png`.
Resumen de esa etapa: `deploy/phase14-summary.md`. El historial se incorpora
en la Fase 15, descrita a continuación.

## Historial clínico · Fase 15

Abrir `http://localhost/patitas/#/acceso` e iniciar sesión con una cuenta
autorizada. Las tres rutas presentan el mismo historial de **solo lectura**:

- Cliente: `#/cliente/historial`, mascotas propias del listado de activas.
  Acceso también desde el panel y desde el detalle de cada mascota.
- Veterinario: `#/veterinario/historial`, mascotas agrupadas desde su agenda.
  La atención clínica incluye un enlace directo al historial de su mascota.
  FastAPI exige que tenga alguna cita asignada a ese profesional; entonces
  permite consultar el historial completo, incluidas atenciones de otros
  veterinarios. Esto no amplía los permisos de edición ni de las citas ajenas.
- Administrador: `#/admin/historial`, selección del listado general de mascotas
  activas. No se habilitan modificaciones clínicas.

Seleccionar mascota y pulsar Consultar historial. Las atenciones aparecen por
fecha descendente; Ver atención completa consulta el detalle con triaje,
diagnóstico, tratamiento, recetas, medicamentos y vacunas. Los valores no
registrados y los historiales vacíos se indican expresamente. Las fechas
DATETIME del contrato se presentan como hora civil de Lima, sin conversión UTC.
Las recetas, detalles y vacunas se agrupan por ID, sin duplicar atenciones ni
confundir medicamentos diferentes con el mismo nombre.

Se utilizan exclusivamente GET `/mascotas/{id}/historial-clinico/` y
GET `/mascotas/{id}/historial-clinico/{id_atencion}` para leer datos clínicos.
La respuesta real contiene mascota y atenciones anidadas; OpenAPI no declara
un response_model detallado para estas rutas. No se utiliza el schema antiguo
como sustituto del contrato de ejecución inspeccionado.

Los enlaces admiten `?id_mascota=ID` y opcionalmente `&id_atencion=ID`.
El servidor vuelve a comprobar propiedad, asignación y correspondencia de la
atención con la mascota. Las selecciones anteriores se retiran antes de consultar
otra y sus solicitudes se cancelan; no se persiste información clínica ni JWT
en localStorage/sessionStorage. Recargar o salir elimina la sesión y la vista.

Limitación existente: los listados de mascotas para cliente/administrador solo
exponen activas; no hay listado de inactivas. La ruta de historial puede resolver
un enlace autorizado a una mascota inactiva, sin que la interfaz adivine IDs.
Los listados no tienen paginación. No se cambió backend, Apache ni MySQL.

Pruebas unitarias e interfaz simulada: los mismos comandos del apartado
Comprobaciones reproducibles. Integración real, solo con autorización para
crear y limpiar el grafo ficticio inventariado:

```powershell
& .\.venv\Scripts\python.exe -B -m backend.tests.integration_phase15_http --run
```

No ejecutar simultáneamente con otras escrituras de prueba. El comando verifica
conteos, IDs y SHA-256 de las 15 tablas al limpiar. Resultados:
`backend/tests/reports/phase15_http.json` y `tests/artifacts/phase15-real.json`;
capturas reales `tests/artifacts/history-*-desktop.png` y `history-*-mobile.png`.
Resumen de esa etapa: `deploy/phase15-summary.md`. La integración general se
describe a continuación.

## Integración general · Fase 16

El recorrido E2E utiliza las interfaces reales del administrador, cliente y
veterinario sobre el mismo grafo ficticio: catálogos y horarios → registro y
mascotas → reserva/reprogramación/cancelación → atención clínica → historial
coincidente en los tres roles. Node conduce Edge con Fetch original; Python
verifica persistencia e inventaría IDs/relaciones en MySQL entre etapas.

Solo con autorización para crear y limpiar datos ficticios y con los servicios
activos y la línea base `backend/tests/reports/phase16_preflight.json` vigente:

```powershell
& .\.venv\Scripts\python.exe -B -m backend.tests.integration_phase16_http --run
```

Se detiene si los datos o definiciones difieren de esa línea base. No ejecutar
simultáneamente con otras escrituras. La limpieza en finally verifica originales,
pertenencia por marcador, relaciones y huellas antes de borrar exclusivamente
el grafo nuevo. Los intentos anteriores ya limpiados se archivan por marcador.

Resultados reales: `backend/tests/reports/phase16_http.json` y
`tests/artifacts/phase16-real.json`. Comparación final independiente:
`backend/tests/reports/phase16_final_verification.json`. Capturas `e2e-*.png`
de escritorio/tableta/móvil son emulación de navegador, no dispositivos físicos.
Pruebas simuladas y unitarias permanecen separadas en phase16-simulated.log y
phase16-unit.log. El JWT efímero de prueba verifica expiración real en cuatro
segundos; no cambia ni sustituye el vencimiento normal de 30 minutos del login.

Las limitaciones conocidas se mantienen: reprogramación con veterinario actual,
ausencia de rechazo explícito de reservas pasadas, perfil de lectura, atención
inicial sin edición y selectores de historial con mascotas activas.
No se modificaron backend/app, esquema MySQL ni Apache durante la Fase 16.

## Evaluación técnica · Fase 17

Evaluación acotada con ISO/IEC 25010:2023 (edición confirmada) y WCAG 2.2;
no equivale a certificación o conformidad completa. Ver `deploy/phase17-summary.md`.
Las correcciones de frontend refuerzan contraste de campos/texto auxiliar y foco
de confirmaciones, sin alterar reglas ni permisos.

Los comandos de regresión habituales siguen disponibles. Las comprobaciones
adicionales de solo lectura del navegador son:

```powershell
node frontend/tests/phase17-precheck.mjs
node frontend/tests/phase17-focus.mjs
node frontend/tests/phase17-load.mjs
```

Las dos primeras guardan evidencia before/after según `PF_AUDIT_STAGE=after`.
No sobrescribir evidencias anteriores al repetirlas sin archivarlas. La medición
de carga usa páginas públicas, caché deshabilitada y tres muestras por ruta.

Solo con autorización para crear/limpiar datos ficticios, servicios activos y
línea base vigente `backend/tests/reports/phase17_preflight.json`:

```powershell
& .\.venv\Scripts\python.exe -B -m backend.tests.integration_phase17_http --run
```

Reutiliza el recorrido E2E de Fase 16 y añade 30 mascotas, 40 citas y 10 atenciones
con prescripciones/vacunas. Peticiones secuenciales, límite de 250 filas nuevas,
inventario entre etapas y limpieza verificada de las 15 tablas. No ejecutar
simultáneamente con otras escrituras. El estado `passed_with_findings` significa
ejecución/limpieza completadas con hallazgos pendientes, no aprobación de seguridad.

Resultados: `backend/tests/reports/phase17_http.json`, `phase17_evaluation.json`
y `phase17_final_verification.json`; auditoría DOM, mediciones y capturas en
`tests/artifacts/phase17-quality.json`, `phase17-load.json` y `quality-*.png`.
Los controles de contraste sin campos se clasifican N/A en la evaluación final.
El backend conserva un hallazgo de confidencialidad en errores 422 que requiere
autorización para corregirse. No se modificaron FastAPI, Apache, esquema o
registros originales. No se inició otra fase ni se generó un informe académico.

## Correcciones finales · Fase 18

Los dos hallazgos anteriores (valores sensibles reflejados en HTTP 422 y
aceptación de reservas pasadas) quedaron corregidos en FastAPI. El frontend
existente presenta los rechazos sin cambios en su código de producción.
También se rechaza reprogramar al pasado según America/Lima. Las demás
limitaciones descritas en fases anteriores se mantienen.

Ver `deploy/phase18-summary.md`, `backend/tests/reports/phase18_http.json` y
`backend/tests/reports/phase18_final_verification.json`: 61 pruebas Python,
41 Node y 34 comprobaciones reales aprobadas en la ejecución final. Todos los
fixtures fueron eliminados y las 15 tablas conservan conteos, IDs y SHA-256
originales. Los intentos interrumpidos se conservan por separado y no se
cuentan como ejecuciones completas aprobadas. No se realizaron pruebas de
caída, recuperación, interrupción ni carga agresiva.
