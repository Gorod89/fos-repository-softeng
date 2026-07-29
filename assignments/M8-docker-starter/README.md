# M8. Docker и CI/CD

Контейнеризируйте небольшой API из этого starter: обеспечьте non-root запуск,
healthcheck, предсказуемую сборку и минимальные права workflow.

```bash
make install
make test
docker compose up --build
curl --fail http://localhost:8000/health
```

Готово, когда образ собирается без секретов, сервис становится healthy,
повторный запуск воспроизводим, `.dockerignore` исключает локальные артефакты,
а CI выполняет test/build/smoke. На защите моделируется отказ сервиса.
