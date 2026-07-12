# INFORME DE AUDITORÍA COMPLETA — RISKORA
### Equipo multidisciplinar: Arquitecto Senior Django/SaaS + Experto PRL + Auditor ISO 45001 + Normativa Española + Analista Funcional + UX/UI

---

## PARTE 1: ESTADO ACTUAL DEL PROYECTO

### 1.1 Lo que ya existe y funciona

| Módulo | Estado | Calidad |
|---|---|---|
| `accounts` — Usuarios y autenticación | Implementado | Bien. Roles definidos (admin/technician/client/auditor/viewer) |
| `companies` — Multiempresa | Implementado | Muy bien. Middleware + context processor + session switching |
| `workcenters` — Centros de trabajo | Implementado | Correcto. CRUD completo con CompanyScopedMixin |
| `workers` — Trabajadores + Puestos | Implementado | Correcto. AJAX para formularios dinámicos |
| `documents` — Control documental | Implementado | Bien. UUID PK, GFK, categorías por alcance, estados |
| `tasks` — Tareas y alertas | Implementado | Bien. Prioridades, GFK, filtros avanzados |
| `training` — Formación | Implementado | Muy bien. 7 modelos, señales, servicios de alertas automáticas |
| `risk_assessment` — Evaluación de riesgos | Implementado | Muy bien. Matriz INSST 3×3, import/export Excel, señales |
| `dashboard` — Panel principal | Implementado | Bien. KPIs, vencimientos, cumplimiento |
| `core` — Mixins y utilidades | Implementado | Bien. `CompanyScopedMixin` sólido |
| UI/UX — `base.html` | Implementado | Muy bien. Diseño profesional, glassmorphism, responsive |

### 1.2 Arquitectura actual

```
Multi-tenancy por empresa (session-based)
├── ActiveCompanyMiddleware → resuelve empresa activa
├── CompanyScopedMixin → filtra querysets automáticamente
├── Superusers → acceso global + switch entre empresas
└── CompanyMembership → roles por empresa
```

### 1.3 Bugs y problemas detectados

| # | Problema | Archivo | Severidad |
|---|---|---|---|
| 1 | `SECRET_KEY` hardcodeada en `base.py` | `config/settings/base.py` | Alta (seguridad) |
| 2 | `Acceso.txt` con credenciales en texto plano en raíz del proyecto | `Acceso.txt` | Alta (seguridad) |
| 3 | Signals de `risk_assessment` **no se conectan** — `apps.py` no define `ready()` ni importa `signals` | `apps/risk_assessment/apps.py` | Alta (funcional) |
| 4 | `HttpResponseRedirect` no importado en `accounts/views.py` pero usado en `RegisterView` y `PasswordChangeView` | `apps/accounts/views.py` | Alta (crash) |
| 5 | `get_form_kwargs` duplicado en `TaskCreateView` | `apps/tasks/views.py` | Baja (_warnings) |
| 6 | `config/db.sqlite3` duplicado junto al `db.sqlite3` de raíz | `config/db.sqlite3` | Baja (limpieza) |
| 7 | `apps/core/views.py` tiene un `DashboardView` legacy sin usar | `apps/core/views.py` | Baja (limpieza) |
| 8 | Mezcla de namespaces: algunas apps tienen `app_name`, otras no | Varios `urls.py` | Media (consistencia) |
| 9 | CSS entero en `base.html` (~800 líneas) sin extraer a archivo `.css` | `templates/base.html` | Media (mantenibilidad) |
| 10 | Sin archivo `.env` — secrets hardcodeados | `config/settings/base.py` | Alta (seguridad) |
| 11 | Base de datos仍为 SQLite — necesita PostgreSQL para SaaS | `config/settings/base.py` | Media (producción) |

---

## PARTE 2: MÓDULOS FALTANTES vs. REQUERIMIENTOS

### 2.1 Mapa completo de módulos necesarios

| # | Módulo | Estado | Prioridad MVP | Complejidad |
|---|---|---|---|---|
| 1 | Empresas | ✅ Existe | — | — |
| 2 | Centros de trabajo | ✅ Existe | — | — |
| 3 | Trabajadores | ✅ Existe | — | — |
| 4 | Puestos de trabajo | ✅ Existe | — | — |
| 5 | Evaluaciones de riesgos | ✅ Existe | — | — |
| 6 | **Planificación preventiva** | ❌ Falta | **Crítica** | Alta |
| 7 | **Equipos de trabajo** | ❌ Falta | **Crítica** | Media |
| 8 | **EPIs** | ❌ Falta | **Crítica** | Media |
| 9 | **Productos químicos** | ❌ Falta | Alta | Alta |
| 10 | **Vigilancia de la salud** | ❌ Falta | **Crítica** | Alta |
| 11 | Formación | ✅ Existe | — | — |
| 12 | **Coordinación de actividades empresariales** | ❌ Falta | Alta | Media |
| 13 | **Emergencias** | ❌ Falta | Alta | Media |
| 14 | **Accidentes e incidentes** | ❌ Falta | **Crítica** | Alta |
| 15 | **Inspecciones** | ❌ Falta | **Crítica** | Media |
| 16 | **Auditorías internas** | ❌ Falta | Alta | Alta |
| 17 | **No conformidades** | ❌ Falta | Alta | Media |
| 18 | **Acciones correctivas** | ❌ Falta (parcial en Tasks) | **Crítica** | Media |
| 19 | Control documental | ✅ Existe | — | — |
| 20 | **Mantenimiento de equipos** | ❌ Falta | Alta | Media |
| 21 | **Requisitos legales** | ❌ Falta | Alta | Alta |
| 22 | **ISO 45001 (mapa de cumplimiento)** | ❌ Falta | Alta | Alta |
| 23 | **Indicadores KPI** | ⚠️ Parcial (dashboard) | Alta | Media |
| 24 | Dashboard | ✅ Existe | — | — |
| 25 | **Notificaciones por email** | ❌ Falta | Alta | Baja |
| 26 | **Generación de PDFs** | ❌ Falta | Alta | Media |
| 27 | **API REST** | ❌ Falta (fase futura) | Baja | Alta |

---

## PARTE 3: NORMATIVA ESPAÑOLA — QUÉ DOCUMENTACIÓN EXIGE CADA RD

### 3.1 Tabla de exigencias documentales por normativa

| Normativa | Documentación obligatoria | Registros a conservar | Frecuencia | Alertas automáticas |
|---|---|---|---|---|
| **Ley 31/1995** (PRL) | Plan de prevención, Evaluación de riesgos, Planificación preventiva, Información a trabajadores | Evaluaciones, planes, comunicaciones ARL | Anual mínimo + cada cambio | Renovación evaluaciones, actualización plan |
| **RD 39/1997** (Servicios Prevención) | Plan de actividad preventiva, Programa anual, Informe anual actividad, Actas reuniones CAE | Programas, informes, actas, datos trabajadores, formación | Anual | Vencimiento informes, actas pendientes |
| **RD 1215/1997** (Equipos trabajo) | Instrucciones uso, Marcado CE, Revisiones periódicas | Registros de revisión, mantenimiento, reparaciones | Cada 3-6 meses según equipo | Próxima revisión equipo |
| **RD 773/1997** (EPIs) | Evaluación necesidad EPI, Certificado CE, Instrucciones uso, Formación uso | Registro entrega EPIs, formación uso, inspecciones | Cada 6-12 meses | Caducidad EPI, próximo recambio |
| **RD 486/1997** (Lugares trabajo) | Evaluación lugares, Condiciones higiénicas, Iluminación, Ruido, Temperatura | Mediciones ambientales, inspecciones | Anual + cada cambio | Vencimiento mediciones |
| **RD 485/1997** (Señalización) | Señalización seguridad, Planos emergencia, Rutas evacuación | Inspecciones señalización | Semestral | Próxima inspección |
| **RD 374/2001** (Agentes químicos) | Evaluación riesgo químico, Fichas seguridad (FDS), EPIs específicos | FDS, registros exposición, vigilancia | Cada cambio de producto | Renovación FDS, nueva sustancia |
| **RD 171/2004** (CAE) | Plan de emergencia, Evacuación, Primeros auxilios, Evaluación riesgos CAE | Ejercicios simulacro, formación, medios | Anual mínimo | Próximo simulacro, renovación plan |
| **RD 614/2001** (Riesgo eléctrico) | Evaluación riesgo eléctrico, Instrucciones, Formación | Registros mantenimiento instalaciones, formación | Anual + cada modificación | Próxima revisión instalación |
| **RD 681/2003** (ATEX) | Evaluación ATEX, Zonas clasificadas, Equipos homologados | Certificados equipos, inspecciones, formación | Anual + cada cambio | Vencimiento certificación ATEX |
| **RD 1627/1997** (Construcción) | Plan de seguridad y salud, Planes de emergencia | Actas reuniones, formación, vigilancia | Por obra | Vencimiento plan |
| **RGPD** | Política privacidad, Consentimientos, DPO | Registros tratamiento, consentimientos | Continuo | Renovación consentimientos |

### 3.2 Requisitos de conservación documental

| Tipo de registro | Plazo mínimo conservación | Base legal |
|---|---|---|
| Evaluación de riesgos | Toda la actividad + 5 años | Art. 23 Ley 31/1995 |
| Plan de prevención | Toda la actividad + 5 años | Art. 16 Ley 31/1995 |
| Formación trabajadores | Toda la actividad + 5 años | Art. 19 Ley 31/1995 |
| Vigilancia de la salud | Toda la actividad + 5 años | Art. 22 Ley 31/1995 |
| Accidentes de trabajo | 20 años (permanente) | Art. 164 LPRL |
| EPIs (entregas y formación) | 5 años mínimo | RD 773/1997 |
| Equipos de trabajo (revisiones) | Vida útil del equipo + 5 años | RD 1215/1997 |
| Agentes químicos (FDS) | 40 años | RD 374/2001 |
| Mediciones ambientales | 5 años | RD 486/1997 |
| Auditorías internas | 5 años | ISO 45001 / Ley 31/1995 |
| No conformidades + acciones correctivas | 5 años | ISO 45001 |
| Datos personales (RGPD) | Durante tratamiento + plazo legal | RGPD Art. 5.1.e) |

---

## PARTE 4: MAPEO ISO 45001:2018 — CUBIERTO vs. PENDIENTE

| Requisito ISO 45001 | Sección | Estado | Qué falta |
|---|---|---|---|
| Contexto de la organización | 4.1-4.4 | ⚠️ Parcial | No hay modelo de "Partes interesadas" ni "Alcance del SG-SST" |
| Liderazgo y compromiso | 5.1-5.4 | ⚠️ Parcial | Falta modelo de "Política SST", "Objetivos SST", "Responsabilidades" |
| Consulta y participación | 5.4 | ❌ Falta | No hay registro de consultas a trabajadores |
| Planificación (riesgos y oportunidades) | 6.1 | ⚠️ Parcial | Evaluación de riesgos existe pero no hay "riesgos y oportunidades del SG-SST" |
| Objetivos SST | 6.2 | ❌ Falta | No hay modelo de objetivos medibles |
| Recursos, competencia, toma de conciencia | 7.1-7.3 | ⚠️ Parcial | Formación existe pero no hay "competencias" ni "toma de conciencia" como proceso |
| Comunicación | 7.4 | ❌ Falta | No hay flujo de comunicación documentado |
| Información documentada | 7.5 | ⚠️ Parcial | Control documental existe pero sin "obligatoriedad" ni "control de cambios" |
| Planificación y control operacional | 8.1-8.2 | ⚠️ Parcial | Evaluación de riesgos + planificación preventiva faltan como flujo integrado |
| Gestión del cambio | 8.1.2 | ❌ Falta | No hay modelo de "Gestión del cambio" |
| Adquisiciones | 8.3 | ❌ Falta | No hay control de proveedores/subcontratistas |
| Emergencias | 8.2 | ❌ Falta | No hay módulo de emergencias |
| Seguimiento y medición | 9.1 | ⚠️ Parcial | KPIs en dashboard pero sin proceso formal de "seguimiento y medición" |
| Evaluación del cumplimiento legal | 9.1.2 | ❌ Falta | No hay módulo de "Requisitos legales" |
| Auditoría interna | 9.2 | ❌ Falta | No hay módulo de auditorías internas |
| Revisión por la dirección | 9.3 | ❌ Falta | No hay modelo de "Revisión por la dirección" |
| No conformidad y acción correctiva | 10.2 | ❌ Falta (parcial en Tasks) | No hay modelo formal de no conformidades con causa-raíz |
| Mejora continua | 10.3 | ❌ Falta | No hay proceso de "mejora continua" documentado |

---

## PARTE 5: DIAGNÓSTICO UX/UI

### Lo que está bien
- Diseño visual muy profesional (glassmorphism, gradientes coherentes)
- Sidebar con iconografía SVG clara
- Responsive con 5 breakpoints
- Sistema de badges semánticos completo (11 variantes)
- Hero section para el dashboard

### Lo que necesita mejora

| Problema | Detalle | Impacto |
|---|---|---|
| CSS inline (~800 líneas en `base.html`) | Difícil de mantener, imposible cachear | Alto |
| Sin framework CSS | Cada componente es custom, falta consistencia | Medio |
| Sin JavaScript organizado | Solo `onchange` inline, sin módulos JS | Alto |
| Sin breadcrumb | Navegación profunda sin orientación | Medio |
| Sin paginación visible | Listas largas sin límite de elementos | Alto |
| Sin búsqueda global | Solo filtros por módulo | Medio |
| Sin loading states | Sin feedback durante operaciones | Bajo |
| Sin confirmación de acciones destructivas | Delete solo con `confirm()` del navegador | Medio |
| Sin sidebar colapsable | Ocupa 276px siempre en desktop | Bajo |
| Sin modo oscuro | Diseño fijo solo claro | Bajo |
| Sin notificaciones toast | Sin feedback post-operación | Medio |

---

## PARTE 6: ROADMAP PROPUESTO — MVP → SAAS PROFESIONAL

### FASE 0: Corrección de bugs críticos (1-2 días)

| Tarea | Descripción |
|---|---|
| 0.1 | Crear archivo `.env` y mover `SECRET_KEY` + secrets ahí |
| 0.2 | Añadir `python-dotenv` a requirements.txt |
| 0.3 | Conectar signals de `risk_assessment` en `apps.py` → `ready()` |
| 0.4 | Corregir imports faltantes en `accounts/views.py` |
| 0.5 | Eliminar `config/db.sqlite3` duplicado y `Acceso.txt` |
| 0.6 | Eliminar `core/views.py` legacy `DashboardView` |
| 0.7 | Añadir `app_name` a todas las apps que carecen de namespace |

### FASE 1: Módulos PRL esenciales — MVP (2-4 semanas)

| Tarea | Módulo | Modelos Django |
|---|---|---|
| 1.1 | **Acciones correctivas formales** | `CorrectiveAction` (no conformidad, causa raíz, acción, responsable, fecha, evidencia, verificación) |
| 1.2 | **Inspecciones** | `Inspection`, `InspectionItem`, `InspectionTemplate` (checklist, centro, resultado, fotos, no conformidad) |
| 1.3 | **Accidentes e incidentes** | `Accident`, `AccidentFactor` (tipo, gravedad, partes, factores, partes trabajadoras, días baja) |
| 1.4 | **EPIs** | `PPE`, `PPEDelivery`, `PPEInspection` (certificate, marca, modelo, caducidad, entrega, inspección) |
| 1.5 | **Equipos de trabajo** | `WorkEquipment`, `EquipmentRevision` (tipo, marca, modelo, revisión, caducidad, mantenimiento) |
| 1.6 | **Vigilancia de la salud** | `HealthSurveillance`, `HealthExam`, `MedicalCertificate` (tipo examen, aptitud, fecha, caducidad, sanitario) |
| 1.7 | **Notificaciones email** | `django.core.mail` + signals → envío automático de alertas por email |
| 1.8 | **Generación de PDFs** | `weasyprint` o `xhtml2pdf` → informes de evaluación, planes, certificados |

### FASE 2: Módulos PRL avanzados (4-8 semanas)

| Tarea | Módulo |
|---|---|
| 2.1 | **Planificación preventiva** (conectado a evaluaciones de riesgos) |
| 2.2 | **Productos químicos** (FDS, clasificación, pictogramas, EPIs asociados) |
| 2.3 | **Coordinación de actividades empresariales** (subcontratistas, mutua, ARL) |
| 2.4 | **Emergencias** (planes, simulacros, medios, formación) |
| 2.5 | **Requisitos legales** (catálogo normativo, checklist cumplimiento, alertas) |
| 2.6 | **No conformidades formales** (con causa-raíz, 5 porqués, Ishikawa) |
| 2.7 | **Mantenimiento de equipos** (preventivo + correctivo,计划) |

### FASE 3: ISO 45001 + Gestión documental avanzada (8-12 semanas)

| Tarea | Módulo |
|---|---|
| 3.1 | **Auditorías internas** (plan, checklist por cláusula, hallazgos, informe) |
| 3.2 | **Política SST + Objetivos** (con indicadores, responsables, plazos) |
| 3.3 | **Gestión del cambio** (evaluación impacto, aprobación, comunicación) |
| 3.4 | **Revisión por la dirección** (actas, indicadores input/output) |
| 3.5 | **Mapa de cumplimiento ISO 45001** (dashboard por cláusula) |
| 3.6 | **Control de proveedores y subcontratistas** |

### FASE 4: SaaS Multiempresa (12-20 semanas)

| Tarea | Descripción |
|---|---|
| 4.1 | Migrar de SQLite a PostgreSQL |
| 4.2 | Implementar `django-tenants` o schema-based multi-tenancy |
| 4.3 | Sistema de suscripciones y planes |
| 4.4 | Panel de administración SaaS |
| 4.5 | Facturación y billing |
| 4.6 | Rate limiting y límites por plan |
| 4.7 | SSL + hardening seguridad |

### FASE 5: IA + BI + Móvil (20+ semanas)

| Tarea | Descripción |
|---|---|
| 5.1 | API REST con DRF |
| 5.2 | IA: generación automática de evaluaciones |
| 5.3 | IA: OCR documental (fotos → datos) |
| 5.4 | IA: chatbot PRL |
| 5.5 | IA: predicción de accidentes |
| 5.6 | App móvil (React Native o Flutter) |
| 5.7 | Business Intelligence (Metabase o custom) |
| 5.8 | Exportación a Excel/PDF avanzada |

---

## PARTE 7: QUÉ HACER AHORA — PASO A PASO

### PASO 1: Corregir los bugs críticos (sin esto nada funciona bien)

```
┌─────────────────────────────────────────────────┐
│  PRIORIDAD MÁXIMA — ANTES DE AÑADIR NADA NUEVO  │
└─────────────────────────────────────────────────┘
```

**Paso 1.1** — Crear archivo `.env` en la raíz del proyecto:
```
SECRET_KEY=tu-clave-secreta-aqui-cambiala
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
```

**Paso 1.2** — Instalar `python-dotenv`:
```bash
pip install python-dotenv
```

**Paso 1.3** — Modificar `config/settings/base.py` para leer de `.env`:
```python
from dotenv import load_dotenv
import os
load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-dev-key')
```

**Paso 1.4** — Conectar signals de `risk_assessment`:
En `apps/risk_assessment/apps.py` añadir:
```python
def ready(self):
    import apps.risk_assessment.signals  # noqa
```

**Paso 1.5** — Corregir imports en `accounts/views.py`:
Añadir `from django.http import HttpResponseRedirect` al inicio.

**Paso 1.6** — Eliminar archivos duplicados: `config/db.sqlite3`, `Acceso.txt`

---

### PASO 2: Crear el primer módulo nuevo — "Acciones Correctivas"

Este es el módulo más crítico para ISO 45001 y para el cumplimiento legal. Ya tienes `tasks` que sirve como base, pero necesitas un modelo formal.

**Paso 2.1** — Crear la app:
```bash
python manage.py startapp corrective_actions
```

**Paso 2.2** — El modelo base sería:
```python
class NonConformity(models.Model):
    company = ForeignKey(Company)
    title = CharField(max_length=200)
    description = TextField()
    source = CharField(choices=[('internal','Interna'),('external','Externa'),('audit','Auditoría'),('complaint','Reclamación')])
    detected_by = ForeignKey(User)
    detected_date = DateField()
    work_center = ForeignKey(WorkCenter, null=True)
    worker = ForeignKey(Worker, null=True)
    status = CharField(choices=[('open','Abierta'),('in_progress','En proceso'),('resolved','Resuelta'),('closed','Cerrada')])
    root_cause = TextField(blank=True)  # 5 porqués / Ishikawa
    corrective_action = TextField()
    responsible = ForeignKey(User, related_name='responsible_actions')
    deadline = DateField()
    effectiveness_verified = BooleanField(default=False)
    effectiveness_date = DateField(null=True)
    verified_by = ForeignKey(User, null=True)
```

**Paso 2.3** — Crear views, forms, urls, templates siguiendo el patrón de `tasks`

**Paso 2.4** — Añadir señal de email cuando se crea una acción correctiva

**Paso 2.5** — Añadir al sidebar de `base.html`

**Paso 2.6** — Añadir al dashboard

---

### PASO 3: Crear "Inspecciones"

```python
class Inspection(models.Model):
    company = ForeignKey(Company)
    work_center = ForeignKey(WorkCenter)
    inspector = ForeignKey(User)
    inspection_date = DateField()
    template = ForeignKey('InspectionTemplate', null=True)
    status = CharField(choices=[('draft','Borrador'),('completed','Completada'),('nonconformity','Con NC')])
    observations = TextField()
    
class InspectionItem(models.Model):
    inspection = ForeignKey(Inspection)
    checklist_item = TextField()
    result = CharField(choices=[('compliant','Conforme'),('noncompliant','No conforme'),('na','No aplica')])
    observations = TextField(blank=True)
    photo = ImageField(null=True)
    non_conformity = ForeignKey('NonConformity', null=True)  # auto-crear NC
```

---

### PASO 4: Crear "Accidentes e incidentes"

```python
class Accident(models.Model):
    company = ForeignKey(Company)
    work_center = ForeignKey(WorkCenter)
    accident_date = DateTimeField()
    description = TextField()
    type = CharField(choices=[('accident','Accidente'),('incident','Incidente'),('near_miss','Cuasi-accidente')])
    gravity = CharField(choices=[('mortal','Mortal'),('grave','Grave'),('leve','Leve'),('sin_baja','Sin baja')])
    injured_workers = ManyToManyField(Worker)
    sick_leave_days = IntegerField(default=0)
    reported_to = BooleanField(default=False)  # comunicado a autoridad laboral
    reported_date = DateField(null=True)
    investigation = TextField(blank=True)
    preventive_measures = TextField(blank=True)
```

---

## RESUMEN EJECUTIVO

| Aspecto | Evaluación |
|---|---|
| **Base técnica** | Sólida. Arquitectura modular bien pensada, multi-tenancy correcta |
| **Calidad de código** | Buena. CBVs consistentes, signals, services, mixins |
| **Cumplimiento PRL** | ~30%. Cubre evaluación riesgos, formación, docs. Falta 70% módulos |
| **Cumplimiento ISO 45001** | ~25%. Falta liderazgo, objetivos, auditorías, NC formales, mejora continua |
| **Normativa española** | ~35%. Falta EPIs, equipos trabajo, químicos, emergencias, accidentes |
| **UX/UI** | Muy buena base visual, pero necesita paginación, búsqueda, breadcrumbs |
| **Preparación SaaS** | 40%. Multi-tenancy base existe, falta PostgreSQL, suscripciones, billing |
| **IA** | 0%. Todo pendiente para fase futura |

### Prioridad inmediata

1. **Corregir bugs** (1-2 días)
2. **Módulo Acciones Correctivas** (1 semana)
3. **Módulo Inspecciones** (1 semana)
4. **Módulo Accidentes/Incidentes** (1 semana)
5. **Módulo EPIs** (3-4 días)
6. **Módulo Equipos de trabajo** (3-4 días)
7. **Módulo Vigilancia de la salud** (1 semana)
8. **Notificaciones email** (2-3 días)
