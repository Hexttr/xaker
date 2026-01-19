#!/usr/bin/env python3
"""
Простой HTTP сервер для тестирования MiroMind API
Эмулирует Anthropic/OpenAI совместимый endpoint
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys

class MiroMindHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/v1/models':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {
                "data": [
                    {
                        "id": "mirothinker-8b",
                        "object": "model",
                        "created": 1234567890,
                        "owned_by": "miromind"
                    }
                ],
                "object": "list"
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/v1/messages':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode())
                prompt = data.get('messages', [{}])[0].get('content', '')
                max_tokens = data.get('max_tokens', 100)
                
                # Простой ответ для тестирования
                response = {
                    "id": "msg-test-123",
                    "type": "message",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Это тестовый ответ от MiroMind. Вы спросили: {prompt[:100]}... (Максимум токенов: {max_tokens})"
                        }
                    ],
                    "model": "mirothinker-8b",
                    "stop_reason": "end_turn",
                    "stop_sequence": None,
                    "usage": {
                        "input_tokens": len(prompt.split()),
                        "output_tokens": max_tokens
                    }
                }
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                error_response = {"error": {"message": str(e), "type": "server_error"}}
                self.wfile.write(json.dumps(error_response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Отключаем стандартное логирование
        pass

def run(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, MiroMindHandler)
    print(f"🧠 MiroMind тестовый сервер запущен на http://localhost:{port}")
    print(f"📡 Endpoint: http://localhost:{port}/v1/messages")
    print(f"📋 Модели: http://localhost:{port}/v1/models")
    print("⚠️  Это тестовый сервер для проверки интеграции")
    print("   Для реальной работы нужна установка SGLang/vLLM и модель MiroThinker")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен")
        httpd.server_close()

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run(port)

