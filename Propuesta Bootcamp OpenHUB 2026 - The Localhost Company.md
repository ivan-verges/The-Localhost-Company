# **Propuesta de Bootcamp: OpenHUB 2026 (UNAPEC)**

## **The Localhost Company: Creating a Startup with your Favorite Local AI Models**

### ---

**Datos Generales del Taller**

> * **Título Oficial:** The Localhost Company: Creating a Startup with your Favorite Local AI Models  
> * **Subtítulo Descriptivo:** Construyendo una Empresa de Software Autónoma (CEO, Analista, Dev y QA) 100% en Contenedores Locales con Paperclip, OpenClaw y Hermes Agent  
> * **Instructor:** Ing. Iván Vergés  
> * **Formato:** Bootcamp Práctico (Hands-on Lab)  
> * **Duración:** 3 horas (09:00 AM – 12:00 PM)  
> * **Fecha:** Sábado 24 de octubre de 2026 (OpenHUB 2026 \- UNAPEC)  
> * **Nivel:** Intermedio (Desarrolladores, SysAdmins, DevOps, QA, Entusiastas de Linux y Open-Source)  
> * **Eje Temático:** Infraestructura Open-Source / IA Local, Contenedores y Soberanía Tecnológica

## **1\. Resumen Ejecutivo (Abstract para Web y Redes Sociales)**

---

*Descargar un modelo de pesos abiertos en tu laptop es genial, pero ponerlo a dirigir una empresa de software completa desde 127.0.0.1 es otro nivel. En este bootcamp práctico de 3 horas construiremos **"The Localhost Company"**: una startup de desarrollo de software 100% autónoma y privada impulsada por tus modelos de IA locales favoritos (vía **Ollama**). Combinando **Paperclip**, **OpenClaw**, **Hermes Agent** y **Playwright MCP** dentro de contenedores Docker en Linux, orquestaremos a un **Agente CEO**, un **Analista de Negocios**, un **Desarrollador** y un **Tester de QA** que colaboran, programan y validan software sin que una sola línea de tu código salga a internet.*

## **2\. Descripción Detallada y Arquitectura (Para el Comité Organizador)**

---

El ecosistema de Inteligencia Artificial en 2026 ha evolucionado de simples asistentes conversacionales a sistemas multi-agente capaces de ejecutar flujos completos de ingeniería de software. Sin embargo, para la comunidad de código abierto y las organizaciones con altos estándares de privacidad, depender de plataformas SaaS cerradas o exponer propiedad intelectual a APIs externas representa una barrera crítica.  
En este taller intensivo construiremos una casa de software virtual que vive íntegramente en localhost. Cada participante actuará como la Junta Directiva (*Human-in-the-loop*) de su propia empresa tecnológica operando sobre cuatro pilares 100% Open-Source:

> * **Paperclip (Plano de Control y Gobernanza):** Define el organigrama corporativo, aloja al **Agente CEO**, administra el estado de los tickets, audita el consumo de cómputo/tokens y establece compuertas de aprobación humana antes de pasar a producción.  
> * **OpenClaw (Operaciones y Análisis de Negocios):** Actúa como el **Agente Analista**, recibiendo objetivos de negocio del CEO y transformándolos en especificaciones técnicas (PRD) y criterios de aceptación estructurados en formato Gherkin.  
> * **Hermes Agent (Ingeniería con Memoria Procedimental):** Impulsa al **Agente Desarrollador**, conectado vía **Model Context Protocol (MCP)** al sistema de archivos y a un repositorio Git local para escribir código y compilar automáticamente nuevas habilidades reutilizables en archivos Markdown (\~/.hermes/skills/).  
> * **Playwright MCP (Aseguramiento de Calidad Autónomo):** Equipa al **Agente de QA** para ejecutar pruebas *End-to-End* (E2E) reales contra el código del Desarrollador. Si una prueba falla, el Agente de QA reporta el *stack trace* al CEO, quien reasigna automáticamente la corrección al Desarrollador hasta que todas las pruebas pasen en verde.

## **3\. Objetivos de Aprendizaje**

---

Al finalizar las 3 horas del bootcamp, cada participante habrá logrado:

> 1. **Desplegar una Arquitectura Multi-Contenedor con Modelos Locales:** Orquestar en Docker Compose sus modelos locales favoritos (**Ollama**: Qwen 2.5 Coder, Llama 3.2, Hermes 3\) junto con **Paperclip** como plano de control central en localhost.  
> 2. **Implementar Orquestación Jerárquica Privada:** Configurar un **Agente CEO** capaz de delegar tareas, supervisar entregables y coordinar la comunicación entre contenedores especializados (Analista, Desarrollador y QA) optimizando las ventanas de contexto locales.  
> 3. **Integrar Herramientas del Sistema Operativo vía MCP:** Conectar modelos locales con herramientas reales de desarrollo (Git local, terminal Linux, sistema de archivos y **Playwright MCP**) manteniendo el aislamiento y la seguridad del *host*.  
> 4. **Automatizar la Memoria Procedimental y el Ciclo Dev ↔ QA:** Lograr que **Hermes Agent** programe una funcionalidad, pase por la validación automática de Playwright y almacene el aprendizaje adquirido en disco para acelerar futuros sprints.

## **4\. Cronograma Detallado (09:00 AM – 12:00 PM)**

---

| Horario | Módulo | Actividades Prácticas y Entregables   |
| :---- | :---- | :---- |
| **09:00 – 09:35** | **1\. Levantando "The Localhost Company" en Docker** | • Despliegue del stack multi-contenedor en Linux/Docker conectando **Ollama** con **Paperclip**. • Selección del modelo local ideal para cada rol (razonamiento para el CEO vs. generación de código para el Dev). • Configuración del organigrama corporativo y reglas del Agente CEO en 127.0.0.1. |
| **09:35 – 10:25** | **2\. Contenedores de Producto e Ingeniería (OpenClaw & Hermes)** | • **El Analista (OpenClaw):** Transformación de un requerimiento de negocio en especificaciones técnicas y casos de prueba usando inferencia local. • **El Desarrollador (Hermes Agent):** Conexión por **MCP** a un repositorio Git local para escribir el código y generar habilidades reutilizables en disco. |
| **10:25 – 10:40** | **Receso / Networking** | • 15 minutos de pausa y asistencia técnica con contenedores e inferencia. |
| **10:40 – 11:30** | **3\. El Contenedor de QA con Playwright MCP** | • Configuración de **Hermes (QA Tester)** conectado a **Playwright MCP** en modo *headless*. • Ciclo cerrado de rebote autónomo en localhost: El CEO envía el código del Dev al QA → el QA ejecuta pruebas E2E → reporta errores al CEO → el Dev corrige el código sin salir de la red local. |
| **11:30 – 12:00** | **4\. Hardening, Optimización y Demo Day en Vivo** | • Buenas prácticas de *sandboxing* para agentes locales con acceso a terminal en Linux. • Simulación de Junta Directiva: Ejecución completa de un sprint en vivo desde localhost, auditoría de métricas en Paperclip y sesión de Q\&A. |

## **5\. Lista de Requisitos Previos para los Participantes (Prerequisite Checklist)**

### ---

**Conocimientos Previos**

> * Manejo básico de la terminal de comandos en Linux/macOS/WSL y conceptos fundamentales de **Git**.  
> * Conocimientos básicos o intermedios de desarrollo de software (JavaScript/TypeScript o Python) y contenedores **Docker**.

### **Checklist de Hardware y Software (Traer instalado el día del evento)**

> * **Laptop personal:** Mínimo **8 GB de RAM** (16 GB recomendados para correr modelos locales con fluidez) y **10 GB de espacio libre en disco**.  
> * **Sistema Operativo:** Distribución Linux nativa, macOS o Windows 10/11 con **WSL2 (Windows Subsystem for Linux)** debidamente activo.  
> * **Docker y Docker Compose:** Instalados y con el servicio activo.  
> * **Entorno de Desarrollo:** **Node.js (v20 LTS+)**, **Python (3.11+)**, **Git** y **Visual Studio Code**.  
> * **Playwright Chromium pre-descargado** (para evitar saturar el Wi-Fi del salón):  
>   npx playwright install chromium  
> * **Ollama instalado (ollama.com)** con al menos un modelo ligero pre-descargado:  
>   ollama pull qwen2.5-coder:3b (o qwen2.5-coder:7b para equipos con 16 GB+ de RAM).

*Nota de Contingencia para el Evento:* El instructor llevará memorias USB 3.0 con las imágenes de Docker, el repositorio base y los modelos de Ollama pre-descargados para instalación *offline* en 2 minutos, además de proveer un *endpoint* de inferencia compartido en la red local para aquellos participantes cuyas laptops tengan recursos limitados de RAM/GPU.

## **6\. Requerimientos Logísticos en el Aula (UNAPEC)**

> * ---

>   Proyector o pantalla con entrada HDMI y buena resolución para lectura de código y diagramas en vivo.  
> * Regletas o tomas de corriente accesibles para los participantes (la ejecución de contenedores e inferencia local demanda alto consumo de batería).