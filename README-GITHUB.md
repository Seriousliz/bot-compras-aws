# 🛒 Bot de Asistencia de Compras

Sistema conversacional inteligente para asistencia de compras de electrodomésticos, desplegado en AWS.

## 🚀 Demo en Vivo

- **API**: `https://2tttwbrm34.execute-api.us-west-2.amazonaws.com/prod/`
- **Health Check**: [/health](https://2tttwbrm34.execute-api.us-west-2.amazonaws.com/prod/health)

## 🏗️ Arquitectura

- **Frontend**: HTML/JS vanilla con interfaz de chat
- **Backend**: AWS Lambda + API Gateway
- **Base de Datos**: DynamoDB para historial
- **Autenticación**: AWS Cognito
- **Almacenamiento**: S3 para archivos de audio

## 🧪 Pruebas

```bash
# Instalar dependencias
pip install requests

# Ejecutar pruebas automatizadas
python test_system.py
```

## 🔧 Despliegue

```bash
# Instalar CDK
npm install -g aws-cdk

# Desplegar infraestructura
cdk deploy
```

## 📱 Frontend Local

```bash
cd frontend
python -m http.server 8080
```

Visita: http://localhost:8080

## 🔐 Credenciales de Prueba

- **Email**: test@example.com
- **Password**: TestPass123!

## 📊 Estado del Proyecto

✅ **Completado**: Infraestructura core, API funcional, frontend operativo
🔄 **Pendiente**: Integraciones IA (Lex, Bedrock, Transcribe, Polly)

---

**Desarrollado con AWS CDK + Python 3.12**
