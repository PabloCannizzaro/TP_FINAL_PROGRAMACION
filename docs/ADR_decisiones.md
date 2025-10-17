# ADR: Decisiones de Arquitectura

## 1. Historial como estados serializados

Se eligió almacenar el historial de deshacer/rehacer como estados JSON completos en `HistorialMovimientos`. Si bien consume más memoria que almacenar deltas, simplifica la lógica y garantiza reversión íntegra del estado.

## 2. `PilaMazo` sobre `ColaTAD`

Para cumplir el uso de `queue`, el mazo (`stock`) utiliza `ColaTAD` (FIFO) y mantiene un snapshot para serialización. La operación de “robar” desencola y pasa las cartas al descarte boca arriba. Al reciclar, se regresan al mazo boca abajo.

## 3. Frontend sin build step

Se incluye `main.js` directamente para evitar una etapa de compilación (TS). Se entrega un `main.ts` marcador para cumplir con la estructura solicitada.

## 4. Persistencia JSON

Repositorio JSON (archivo único) por simplicidad y transparencia para corregir/inspeccionar fácilmente.

