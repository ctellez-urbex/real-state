#!/bin/bash

# Script para configurar variables de entorno localmente

echo "🔧 Configurando variables de entorno para Urbex API..."

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    cp env.example .env
    echo "✅ Archivo .env creado desde env.example"
fi

# API Keys generadas
API_KEYS='["urbex-prod-key-pPK5CrbFX7Ue9u3gWvJc-A","urbex-dev-key-pOV9-fe9HSKdI3tfogdUIw","urbex-test-key-vjtyZHsCM2VpR_iGptzRxw"]'

# Actualizar API_KEYS en .env
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s/API_KEYS=.*/API_KEYS=$API_KEYS/" .env
else
    # Linux
    sed -i "s/API_KEYS=.*/API_KEYS=$API_KEYS/" .env
fi

echo "✅ API Keys configuradas en .env"
echo ""
echo "🔑 API Keys disponibles:"
echo "  - urbex-prod-key-pPK5CrbFX7Ue9u3gWvJc-A (Producción)"
echo "  - urbex-dev-key-pOV9-fe9HSKdI3tfogdUIw (Desarrollo)"
echo "  - urbex-test-key-vjtyZHsCM2VpR_iGptzRxw (Testing)"
echo ""
echo "📝 Para usar en Postman, agrega el header:"
echo "   x-api-key: urbex-test-key-vjtyZHsCM2VpR_iGptzRxw"
echo ""
echo "🚀 Para ejecutar localmente:"
echo "   make run"
