# MEMORIA DEL PROYECTO RISKORA

**Gestión Integral de Prevención de Riesgos Laborales (PRL)**

Versión del documento: 1.0
Fecha: 13 de julio de 2026
Último commit: `e9022e9` — Evaluación de Riesgos: split por tipo + informes especiales

---

## 1. Resumen Ejecutivo

**Riskora** es una plataforma SaaS para la gestión integral de Prevención de Riesgos Laborales (PRL) dirigida a PYMES, consultorías y servicios de prevención en España. Cubre la totalidad del ciclo de gestión de la seguridad laboral según la normativa española vigente (Ley 31/1995 de Prevención de Riesgos Laborales, RD 39/1997, guías INSST).

La aplicación está diseñada para ser utilizada por técnicos de prevención, responsables de seguridad en la empresa y auditores. Permite gestionar múltiples empresas desde una única instancia, con aislamiento completo de datos por compañía.

### Características principales

- **Multi-tenant**: aislamiento de datos por empresa con selector de compañía en tiempo real
- **17 módulos funcionales** cubriendo todos los aspectos de la PRL
- **Metodología INSST**: matriz de probabilidad × severidad para evaluación de riesgos
- **Generación de PDFs**: informes de investigación de accidentes, EEPP, registros de EPIs
- **Importación/Exportación Excel**: para evaluaciones de riesgos y planificación preventiva
- **Interfaz en español**: diseño profesional con sidebar de navegación oscuro

---

## 2. Arquitectura y Tecnología

### Stack tecnológico

| Componente | Tecnología |
|---|---|
| Framework | Django 6.0.5 |
| Python | 3.10+ |
| Base de datos (dev) | SQLite3 |
| Base de datos (prod) | SQLite3 (pendiente migración a PostgreSQL) |
| Plantillas | Django Template Language + CSS inline |
| PDF | ReportLab >= 4.0 |
| Excel | openpyxl >= 3.1.0 |
| Variables de entorno | python-dotenv >= 1.0.0 |
| Servidor (dev) | Django development server |
| Servidor (prod) | WSGI/ASGI configurable |

### Estructura de configuración

```
config/
├── settings/
│   ├── base.py      ← Configuración compartida (22 apps locales)
│   ├── dev.py       ← DEBUG=True, localhost
│   └── prod.py      ← DEBUG=False, placeholder ALLOWED_HOSTS
├── urls.py          ← 25+ URL namespaces
├── wsgi.py
└── asgi.py
```

### Multi-tenancy

El sistema utiliza un patrón de multi-tenancy basado en FK:

1. **Modelo de datos**: Cada modelo operativo tiene un campo `empresa` (FK → Company)
2. **Mixin `CompanyScopedMixin`** (`apps/core/mixins.py`): Filtra automáticamente los querysets por la empresa activa del usuario
3. **Middleware `ActiveCompanyMiddleware`** (`apps/companies/middleware.py`): Inyecta `request.active_company` desde la sesión
4. **Context Processor**: Expone `active_company`, `company_membership` y `available_companies` a todas las plantillas
5. **Selector de empresa**: Visible en el topbar, permite cambiar de empresa en tiempo real. Superusuarios sin empresa ven un placeholder amarillo

### Diseño visual (CSS inline)

Todo el sistema de diseño está embebido en `base.html` (~800+ líneas CSS). No se utilizan frameworks CSS externos (ni Bootstrap ni Tailwind). Características:

- Variables CSS para theming (`--primary`, `--blue`, `--purple`, `--danger`, etc.)
- Sidebar oscuro con degradado radial y estados activos
- Layout grid: sidebar 276px + contenido flexible
- Sistema de tarjetas de módulo con barras de acento de degradado
- Badges de nivel de riesgo con colores por severidad
- Formularios con estilos consistentes
- Breakpoints responsive: 1250px, 900px, 768px, 640px

### Autenticación

| Configuración | Valor |
|---|---|
| Modelo de usuario | `accounts.User` (AbstractUser) |
| Roles de usuario | admin, technician, client, auditor, viewer |
| Roles de membresía | company_admin, technician, manager, reader |
| LOGIN_URL | `/login/` |
| LOGIN_REDIRECT_URL | `/` |

---

## 3. Módulos Funcionales

### 3.1 Datos de Empresa

| Módulo | URL | Namespace | Modelos | Funcionalidad |
|---|---|---|---|---|
| **Empresas** | `/empresas/` | `companies` | Company, CompanyMembership | CRUD completo, selector de empresa, switch entre empresas |
| **Centros de trabajo** | `/centros/` | `workcenters` | WorkCenter | CRUD con niveles de riesgo, contacto, actividad |
| **Trabajadores** | `/trabajadores/` | `workers` | Worker, JobPosition | CRUD trabajadores + puestos de trabajo, campos DNI/NIE, SS |
| **Datos empresa** | `/datos-empresa/` | `company_data` | — | Dashboard resumen con conteos de centros, trabajadores, puestos, equipos |

### 3.2 Gestión PRL

| Módulo | URL | Namespace | Modelos | Funcionalidad |
|---|---|---|---|---|
| **Evaluación de Riesgos** | `/evaluaciones/` | `risk_assessment` | EvaluacionRiesgos, ItemEvaluacionRiesgos, TipoPeligro, NivelRiesgoReferencia, InformeRiesgoEspecial | Dashboard por tipo (evitable/monitorizable/no_evitable), matriz INSST, import/export Excel, informes especiales (higiénico/psicosocial/ergonómico) |
| **Planificación Preventiva** | `/planificacion/` | `preventive_planning` | ItemPlanificacion | CRUD items, import/export Excel, enlace a evaluaciones de riesgos |
| **Plan de Prevención** | `/plan-prevencion/` | `prevention_plan` | PlanPrevention | 6 secciones: política, organigrama, delegado PRL, recurso preventivo, funciones, ETT/teletrabajo. Auto-creación al crear empresa |
| **Acciones Correctivas** | `/nc/` | `corrective_actions` | NoConformidad, AccionCorrectiva, AccionPreventiva | Gestión de NC con causas raíz (5 porques, Ishikawa), acciones correctivas y preventivas |
| **Inspecciones** | `/inspecciones/` | `inspecciones` | PlantillaInspeccion, PlantillaInspeccionItem, Inspeccion, ItemInspeccion | Plantillas reutilizables, inspecciones con items, generación de NC desde items |
| **CAE** | `/cae/` | `cae` | EmpresaSubcontrata, DocumentoCAETipo, DocumentoCAE, ProcedimientoCAE, CartaCAE, DocumentoRiesgosCAE | Coordinación de actividades empresariales, 12 tipos de documentos, progreso de documentación |

### 3.3 Seguridad y Accidentes

| Módulo | URL | Namespace | Modelos | Funcionalidad |
|---|---|---|---|---|
| **Investigación de Accidentes** | `/seguridad/` | `incidents` | Accidente, InvestigacionAccidente, ProcedimientoInvestigacion, CausaAccidente, Incidente | Dashboard 4 tarjetas, investigación detallada (16+ campos), PDF investigación, causas (inmediatas/básicas/organizativas) |
| **Enfermedades Profesionales** | `/eepp/` | `epps` | EnfermedadProfesional, InvestigacionEEPP, ProcedimientoInvestigacionEEPP | CRUD + investigación con 16 elecciones de riesgo, PDF investigación |
| **Incidentes** | `/seguridad/incidentes/` | `incidents` | Incidente | CRUD incidentes con gravedad potencial, estado, seguimiento |

### 3.4 Equipos y Protección

| Módulo | URL | Namespace | Modelos | Funcionalidad |
|---|---|---|---|---|
| **EPIs** | `/epis/` | `epis` | CatalogoEPI, EPI, EntregaEPI, InspeccionEPI, ProcedimientoEntrega, FirmaEntrega | Catálogo de mercado (24 items), inventario, entregas con firma, inspecciones, registro PDF |
| **Equipos de Trabajo** | `/equipos/` | `work_equipment` | TipoEquipo, EquipoTrabajo, RevisionEquipo, MantenimientoEquipo | Inventario con documentos (manual, CE, certificado), revisiones, mantenimiento preventivo/correctivo/predictivo |

### 3.5 Formación y Documentos

| Módulo | URL | Namespace | Modelos | Funcionalidad |
|---|---|---|---|---|
| **Formación** | `/training/` | `training` | TrainingCategory, TrainingCourse, TrainingRecord, TrainingDocument, TrainingRequirement, TrainingNeed, TrainingAlert | Dashboard, categorías, cursos, registros con vencimiento, alertas automáticas |
| **Documentos** | `/documents/` | `documents` | DocumentCategory, Document | Gestión documental con categorías, versionado, estado, caducidad, GenericForeignKey |
| **Instrucciones de Trabajo** | `/instrucciones-trabajo/` | `work_instructions` | InstruccionTrabajo | CRUD con código, puesto de trabajo asociado, archivo adjunto |

### 3.6 Emergencias y Químicos

| Módulo | URL | Namespace | Modelos | Funcionalidad |
|---|---|---|---|---|
| **Medidas de Emergencia** | `/emergencias/` | `emergency_measures` | MedioProteccionIncendios, EmpresaMedioProteccion, PlanAutoproteccion, EquipoEmergencia, MiembroEquipoEmergencia, RegistroSimulacro, EntregaInformacionEmergencia | Plan de autoprotección, medios de protección (20 catálogo), equipos emergencia, simulacros, entregas de información |
| **Productos Químicos** | `/quimicos/` | `chemical_products` | ProductoQuimico, ClasificacionQuimica | CRUD con ficha de seguridad, clasificación GHS (pictogramas GHS01-GHS09), frases de riesgo |

### 3.7 Salud y Tareas

| Módulo | URL | Namespace | Modelos | Funcionalidad |
|---|---|---|---|---|
| **Vigilancia de la Salud** | `/vigilancia-salud/` | `health_surveillance` | ReconocimientoMedico, ControlSalud | Reconocimientos médicos (inicial/periodico/especial/aptitud), controles de salud |
| **Tareas y Alertas** | `/tasks/`, `/alertas/` | `tasks` | Task, Alert | CRUD tareas con prioridad, alertas por caducidad de documentos, vencimiento formación, etc. |

---

## 4. Modelos de Datos

### Inventario completo (~60 modelos)

| App | Modelos | Relaciones principales |
|---|---|---|
| accounts | User | — |
| companies | Company, CompanyMembership | User ↔ Company (M2M через Membership) |
| workcenters | WorkCenter | Company |
| workers | JobPosition, Worker | Company, WorkCenter, User |
| training | TrainingCategory, TrainingCourse, TrainingRecord, TrainingDocument, TrainingRequirement, TrainingNeed, TrainingAlert | Company, Worker, JobPosition, Course, Document |
| documents | DocumentCategory, Document | Company, User, GenericFK |
| tasks | Task, Alert | Company, User, GenericFK |
| risk_assessment | TipoPeligro, EvaluacionRiesgos, ItemEvaluacionRiesgos, NivelRiesgoReferencia, InformeRiesgoEspecial | Company, WorkCenter, JobPosition, User |
| corrective_actions | NoConformidad, AccionCorrectiva, AccionPreventiva | Company, WorkCenter, Worker, User |
| inspections | PlantillaInspeccion, PlantillaInspeccionItem, Inspeccion, ItemInspeccion | Company, WorkCenter, User, NoConformidad |
| incidents | CausaAccidente, Accidente, InvestigacionAccidente, ProcedimientoInvestigacion, Incidente | Company, WorkCenter, Worker, User, NoConformidad |
| epps | EnfermedadProfesional, InvestigacionEEPP, ProcedimientoInvestigacionEEPP | Company, WorkCenter, Worker |
| epis | CatalogoEPI, EPI, EntregaEPI, InspeccionEPI, ProcedimientoEntrega, FirmaEntrega | Company, Worker, User |
| work_equipment | TipoEquipo, EquipoTrabajo, RevisionEquipo, MantenimientoEquipo | Company, User |
| preventive_planning | ItemPlanificacion | Company, EvaluacionRiesgos |
| prevention_plan | PlanPrevention | Company (1:1) |
| cae | EmpresaSubcontrata, DocumentoCAETipo, DocumentoCAE, ProcedimientoCAE, CartaCAE, DocumentoRiesgosCAE | Company |
| emergency_measures | MedioProteccionIncendios, EmpresaMedioProteccion, PlanAutoproteccion, EquipoEmergencia, MiembroEquipoEmergencia, RegistroSimulacro, EntregaInformacionEmergencia | Company, Worker |
| chemical_products | ProductoQuimico, ClasificacionQuimica | Company |
| health_surveillance | ReconocimientoMedico, ControlSalud | Company, Worker |
| work_instructions | InstruccionTrabajo | Company, JobPosition |

---

## 5. Infraestructura Compartida

### 5.1 CompanyScopedMixin

Ubicación: `apps/core/mixins.py`

Proporciona filtrado automático por empresa en todas las vistas. Comportamiento:
- **Superusuarios**: ven datos de todas las empresas (o la seleccionada vía sesión)
- **Usuarios normales**: solo ven datos de su empresa activa
- **Configuración**: `company_field_name` personalizable (default: `company`)

### 5.2 Arquitectura de Señales (9 archivos)

| App | Señal | Trigger | Acción |
|---|---|---|---|
| prevention_plan | post_save Company | Empresa creada | Auto-crear PlanPrevention con valores por defecto |
| risk_assessment | pre_save ItemEvaluacionRiesgos | Item guardado | Calcular grado_riesgo = probabilidad × severidad |
| training | post_save TrainingRecord | Registro actualizado | Refrescar alertas de formación |
| epis | post_save EntregaEPI | Entrega creada/modificada | Actualizar estado del EPI (asignado/disponible) |
| epps | post_save EnfermedadProfesional | EP guardada | Crear alerta si gravedad = grave/muy_grave |
| incidents | post_save Accidente | Accidente guardado | Crear alerta si baja_permanente/mortal |
| corrective_actions | post_save NoConformidad | NC guardada | Crear alerta para la NC |
| corrective_actions | post_save AccionCorrectiva | AC guardada | Crear alerta al asignar responsable |

### 5.3 Commands de Gestión (5)

| Comando | App | Propósito |
|---|---|---|
| `seed_pasteleria` | core | Datos demo: Pastelería Conde Melero (ID=2) con usuarios, centros, trabajadores, formación, documentos, evaluaciones, NCs, EPIs, equipos, planificación |
| `check_document_alerts` | tasks | Genera alertas por documentos vencidos o por vencer (30 días) |
| `populate_catalogo` | epis | Puebla catálogo de EPIs de mercado (24 items: guantes, cascos, calzado, etc.) |
| `refresh_training_statuses` | training | Refresca estados y alertas de registros de formación |
| `seed_medidas_emergencia` | emergency_measures | Crea 20 tipos de protección contra incendios + 5 categorías de formación |

### 5.4 Servicios

| App | Funciones | Propósito |
|---|---|---|
| `risk_assessment.services` | `calcular_grado_riesgo()`, `calcular_estadisticas_evaluacion()` | Matriz INSST, estadísticas |
| `dashboard.services` | `build_dashboard_context()` | Agregación de KPIs globales |
| `training.services` | `refresh_training_alerts_for_record()` | Generación de alertas de formación |
| `corrective_actions.services` | `crear_alerta_nc()`, `crear_alerta_accion_correctiva()` | Alertas de NC y acciones |
| `epis.services` | `calcular_estadisticas_epis()` | Estadísticas de EPIs |
| `epps.services` | `generar_codigo_eepp()`, `calcular_estadisticas_eepp()`, `generar_pdf_eepp*()` | Código automático, stats, PDFs |

### 5.5 Generación de PDFs (ReportLab)

- **Investigación de accidentes**: formulario en blanco + informe rellenado
- **Investigación de EEPP**: formulario en blanco + informe rellenado
- **Registro de entregas de EPIs**: listado de entregas con firmas

### 5.6 Importación/Exportación Excel (openpyxl)

- **Evaluación de riesgos**: importación con detección flexible de cabeceras, exportación con matriz INSST
- **Planificación preventiva**: importación/exportación de items de planificación

### 5.7 Estructura de Archivos Subidos

Todos los archivos se organizan bajo `media/` con rutas lógicas:

```
media/
├── companies/logos/{pk}/
├── documents/company_{id}/{category_slug}/
├── training/documents/
├── corrective_actions/evidencias/, acciones/
├── inspecciones/fotos/, items/
├── epis/catalogo/, procedimientos/, firmas/
├── equipos/manuales/, declaraciones_ce/, certificados_instalacion/
├── medidas_emergencia/plan/, simulacros/
├── cae/{empresa_id}/
├── fichas_seguridad/, etiquetas_quimicos/
├── reconocimientos_medicos/, controles_salud/
├── instrucciones_trabajo/
├── plan_prevencion/{company_id}/
└── evaluacion_riesgos/especiales/
```

---

## 6. Estado del Código

### 6.1 Historial de Git (17 commits)

```
e9022e9 feat: Evaluación de Riesgos — split por tipo + informes especiales
62c174d feat: módulo medidas de emergencia completo
db13c90 feat: reorganizar sidebar + 5 módulos nuevos
c52aca4 feat: módulos Plan de Prevención y CAE + fix selector de empresa
bd2f971 feat: módulo de Planificación de la Actividad Preventiva
c427fc6 feat: módulo investigación EEPP + mejora investigación accidentes
46a68f3 feat: dashboard de investigación con navegación
dac33cc feat: redesign dashboard con 12 módulos
65555b9 feat: campos documentos en equipos de trabajo
192f72d feat: módulo EPIs completo
be9c10e feat: módulo accidentes e incidentes + inspecciones
555197a feat: lógica de evaluación de riesgo y templates
96abd5d feat: Riskora base — modelos, señales y templates
87d6566 feat: primer commit
53aa886 feat: initial commit
```

### 6.2 Estado de Testing

**Estado: Mínimo/Sin implementar**

- 11 archivos `tests.py` existentes, todos con el scaffolding por defecto de Django
- **No hay tests escritos** en ningún módulo
- No hay framework de testing adicional instalado
- No hay configuración de cobertura de código

### 6.3 Dependencias

```
Django==6.0.5
openpyxl>=3.1.0
reportlab>=4.0
python-dotenv>=1.0.0
```

No hay: DRF, Celery, Redis, psycopg2, whitenoise, gunicorn, docker.

### 6.4 Base de datos

- **Desarrollo**: SQLite3 (`db.sqlite3`)
- **Producción**: SQLite3 (configurado en `prod.py` pero sin migrar)
- **Migraciones**: 23 archivos de migración (0001-0005 en risk_assessment, etc.)

### 6.5 Datos de Prueba

- Empresa: **Pastelería Conde Melero** (ID=2)
- Usuario: `pasteleria` / `Pasteleria2026!`
- Incluye: 2 centros de trabajo, 8+ puestos, 6+ trabajadores, cursos de formación, documentos, evaluaciones de riesgos, NCs, EPIs, equipos, items de planificación

---

## 7. Recomendaciones de Mejora

### Prioridad Alta (Funcionalidad crítica)

| # | Mejora | Descripción | Impacto |
|---|---|---|---|
| 1 | **Tests unitarios y de integración** | Escribir tests para modelos, vistas, forms y servicios de cada módulo. Cobertura mínima objetivo: 60% | Fiabilidad, regresiones, mantenibilidad |
| 2 | **Base de datos PostgreSQL** | Migrar de SQLite a PostgreSQL para producción. SQLite no soporta concurrencia ni escalabilidad | Escalabilidad, concurrencia |
| 3 | **Permisos granulares por rol** | Implementar sistema de permisos basado en roles (company_admin puede todo, technician solo lectura+edición, reader solo lectura) | Seguridad, control de acceso |
| 4 | **Auditoría y logging** | Registro de acciones de usuario (quién creó/editó/borró qué y cuándo). Log de actividad para compliance | Trazabilidad, compliance |
| 5 | **Notificaciones por email** | Alertas vía email para vencimientos de documentos, formación, revisión de equipos, accidentes graves | Proactividad |

### Prioridad Media (Calidad y escalabilidad)

| # | Mejora | Descripción | Impacto |
|---|---|---|---|
| 6 | **REST API con DRF** | API RESTful para integración con apps móviles, sistemas externos, automatizaciones | Integrabilidad |
| 7 | **Cache con Redis** | Cache de dashboards, consultas frecuentes, sesiones | Rendimiento |
| 8 | **Tareas asíncronas con Celery** | Envío de emails, generación de PDFs en background, check de alertas periódico | UX, rendimiento |
| 9 | **Docker + docker-compose** | Containerización para despliegue consistente | DevOps, portabilidad |
| 10 | **CI/CD** | Pipeline automatizado: lint, tests, build, deploy | Calidad, velocidad de despliegue |

### Prioridad Baja (Mejoras de experiencia)

| # | Mejora | Descripción | Impacto |
|---|---|---|---|
| 11 | **Dashboard con gráficas** | Chart.js o similar para visualización de tendencias, distribución de riesgos, evolución temporal | Analítica visual |
| 12 | **Responsive completo** | Revisar y mejorar la experiencia en móvil y tablets | Usabilidad móvil |
| 13 | **Accesibilidad (WCAG 2.1)** | Labels ARIA, contraste, navegación por teclado, screen readers | Accesibilidad legal |
| 14 | **Internacionalización (i18n)** | Preparar el código para soporte multi-idioma (marcar strings con `gettext`) | Escalabilidad internacional |
| 15 | **Autenticación de dos factores (2FA)** | Opción de 2FA para cuentas con rol admin/technician | Seguridad |
| 16 | **Exportación a PDF de dashboards** | PDFs descargables de dashboards de módulos para presentaciones | Utilidad |

---

## 8. Cronograma de Implementación

### Fase 1 — Estabilización (Semanas 1-4)

**Objetivo**: Bases sólidas para escalabilidad

| Semana | Tarea | Detalle |
|---|---|---|
| 1 | Tests unitarios — Modelos | Tests para todos los modelos: validaciones, propiedades, relationships. Cobertura modelos: 80% |
| 2 | Tests unitarios — Vistas | Tests para vistas CRUD principales: status codes, permisos, context, redirects. Cobertura vistas: 60% |
| 3 | Tests de integración | Flujos completos: crear empresa → centro → trabajador → evaluación → NC. Fix de bugs encontrados |
| 4 | Migración PostgreSQL | `docker-compose.yml` con PostgreSQL 16 + Redis. Configurar `prod.py` para usar psycopg2. Migrar datos de SQLite |

### Fase 2 — Seguridad y Auditoría (Semanas 5-8)

**Objetivo**: Control de acceso robusto y trazabilidad

| Semana | Tarea | Detalle |
|---|---|---|
| 5 | Permisos por rol | Implementar `PermissionRequiredMixin` con lógica: admin=todo, technician=CRUD, reader=read-only. Aplicar a todas las vistas |
| 6 | Auditoría de actividad | Modelo `AuditLog` (user, action, model, object_id, timestamp, changes). Signal en cada modelo para registrar cambios |
| 7 | Notificaciones email | Configurar email backend (SMTP/SES). Templates de email para: vencimiento documentos, formación, accidentes graves, NC abiertas |
| 8 | 2FA y seguridad | django-otp o similar para 2FA. Rate limiting en login. Session timeout configurable |

### Fase 3 — API e Integración (Semanas 9-14)

**Objetivo**: API RESTful para integraciones

| Semana | Tarea | Detalle |
|---|---|---|
| 9-10 | DRF setup + serializers | Instalar DRF, crear serializers para: Company, Worker, EvaluacionRiesgos, ItemEvaluacionRiesgos, NoConformidad |
| 11-12 | API views + pagination | ViewSets para todos los módulos principales. Filtros, búsqueda, paginación. Token authentication |
| 13 | API docs | Swagger/OpenAPI con drf-spectacular. Documentación auto-generada |
| 14 | Webhooks | Sistema de webhooks para eventos: accidente grave, NC abierta, documento vencido |

### Fase 4 — Rendimiento y DevOps (Semanas 15-18)

**Objetivo**: Escalabilidad y despliegue automatizado

| Semana | Tarea | Detalle |
|---|---|---|
| 15 | Cache con Redis | Cache de dashboards (TTL 5min), consultas frecuentes (TTL 1h), sesiones |
| 16 | Celery + tareas async | Envío de emails async, generación de PDFs en background, cron job para check de alertas (diario) |
| 17 | Docker completo | `Dockerfile` multi-stage, `docker-compose.yml` (django + postgres + redis + nginx). Variables de entorno |
| 18 | CI/CD | GitHub Actions: lint (ruff), tests (pytest), build docker, deploy a staging. Pipeline a producción manual |

### Fase 5 — Experiencia de Usuario (Semanas 19-22)

**Objetivo**: Mejoras de usabilidad y accesibilidad

| Semana | Tarea | Detalle |
|---|---|---|
| 19 | Dashboard con gráficas | Chart.js: gráfico de riesgos por nivel (donut), tendencia de accidentes (línea), distribución por centro (barras), formación por vencer (timeline) |
| 20 | Responsive móvil | Revisar todos los templates: tablas responsive, formularios móviles, sidebar colapsable, cards adaptativas |
| 21 | Accesibilidad WCAG 2.1 | Labels ARIA, roles, contraste 4.5:1 mínimo, tabindex, skip links, screen reader testing |
| 22 | Internacionalización | `django.middleware.locale`, `gettext` en templates y modelos. Preparar para español + catalán + euskera |

### Fase 6 — Funcionalidad Avanzada (Semanas 23-26)

**Objetivo**: Funcionalidades diferenciadoras

| Semana | Tarea | Detalle |
|---|---|---|
| 23 | Exportación PDF de dashboards | PDFs descargables de resúmenes de módulos para reuniones de comité |
| 24 | Firma digital de documentos | Integración con sistema de firma (o al menos firma con uploaded signature image) |
| 25 | Calendario de prevención | Vista calendario con: vencimientos, revisiones, inspecciones, formaciones, simulacros |
| 26 | Panel de analytics | Métricas globales: tiempo medio resolución NC, % formación al día, tendencia accidentes, ROI preventivo |

---

## 9. Métricas del Proyecto (a la fecha)

| Métrica | Valor |
|---|---|
| Total de apps Django | 22 locales + 6 builtins |
| Total de modelos | ~60 |
| Total de templates HTML | 130+ |
| Total de URLs registradas | 25+ namespaces, 200+ patrones |
| Total de management commands | 5 |
| Total de archivos CSS externos | 0 (todo inline en base.html) |
| Total de archivos JS externos | 0 (mínimo JS inline) |
| Total de commits | 17 |
| Archivos de test escritos | 0 (solo scaffolding) |
| Dependencias externas | 4 (Django, openpyxl, reportlab, python-dotenv) |
| Líneas de CSS estimadas | 800+ (en base.html) |

---

*Documento generado automáticamente el 13 de julio de 2026.*
*Proyecto Riskora — GitHub: https://github.com/Alconde/riskora*
