# 🛡️ Ollama Gemma Secure Auth API

Este proyecto es una API sencilla y segura que sirve como puerta de acceso a Ollama (modelos como Gemma), agregando autenticación, control de uso y protección básica.

La idea es no exponer Ollama directamente, sino acceder a él de forma controlada.

⸻

🚀 ¿Para qué sirve?
	•	Permite enviar mensajes a un modelo de Ollama
	•	Protege el acceso usando un token
	•	Limita el número de solicitudes por usuario
	•	Evita abusos y accesos no autorizados
	•	Puede usarse detrás de Nginx, una UI web o cualquier cliente HTTP

⸻

🔐 Seguridad incluida

Este servicio añade varias capas simples de seguridad:
	•	Token Bearer obligatorio
Solo quien tenga el token correcto puede usar la API.
	•	Rate limit por IP
Cada usuario tiene un número máximo de solicitudes por hora.
	•	Validación básica de datos
Evita mensajes vacíos o inválidos.

⸻

📡 Endpoints disponibles

/validate

Sirve para comprobar si el token es válido.
Útil para integrarlo con proxies como Nginx.

/chat

Envía un mensaje al modelo de Ollama y devuelve la respuesta.

/models

Lista los modelos disponibles en Ollama.

/health

Verifica si Ollama está activo y accesible.

/

Endpoint básico de información.

⸻

⚙️ Variables de entorno

Puedes configurar el servicio usando variables de entorno:
	•	OLLAMA_URL → URL de Ollama
	•	AUTH_TOKEN → Token de acceso
	•	RATE_LIMIT_PER_HOUR → Límite de requests por hora

Si no se definen, el servicio usa valores por defecto.

⸻


## Ejemplos de uso 

```bash 
curl -X POST http://localhost:8080/chat \
-H "Authorization: Bearer SECRET_TOKEN" \
-H "Content-Type: application/json" \
-d '{"message": "Hola Gio", "model": "gemma:2b"}' | jq -r
```

Response: 

```json

  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   615  100   570  100    45     70      5  0:00:09  0:00:08  0:00:01   147


{
  "model": "gemma:2b",
  "created_at": "2026-02-01T22:26:45.697735334Z",
  "response": "Hola Gio! Soy tu amigo Gio. ¿Qué puedo hacer para ayudarte hoy?",
  "done": true,
  "done_reason": "stop",
  "context": [
    968,
    2997,
    235298,
    559,
    235298,
    15508,
    235313,
    1645,
    108,
    18315,
    22758,
    107,
    235248,
    108,
    235322,
    2997,
    235298,
    559,
    235298,
    15508,
    235313,
    2516,
    108,
    18315,
    22758,
    235341,
    43050,
    2575,
    33798,
    22758,
    235265,
    6742,
    13499,
    39952,
    9081,
    1301,
    86852,
    20136,
    235336
  ],
  "total_duration": 7974776073,
  "load_duration": 3512325488,
  "prompt_eval_count": 24,
  "prompt_eval_duration": 2574969730,
  "eval_count": 17,
  "eval_duration": 1857414760
}
```


⸻

### Cómo ejecutarlo

$ python main.py
```bash
docker-compose up --build
```

⸻
 
🧩 Casos de uso comunes
- Backend seguro para una UI web (Streamlit, frontend, etc.)
- Servicio intermedio detrás de Nginx
- Exponer Ollama de forma segura en una red interna
- Probar modelos sin riesgo de abuso

⸻

✅ Resumen

✔ Protege Ollama
✔ Fácil de usar
✔ No expone el modelo directamente
✔ Ideal para pruebas, demos o entornos controlados

⸻
