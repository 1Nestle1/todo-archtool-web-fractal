"""Состав проекта для archtool: список модулей (APPS) и список слоёв (app_layers).

`APPS` — bounded-контексты, которые сканирует `DependencyInjector`.
`app_layers` — все 4 дефолтных слоя Clean Architecture в порядке
outermost → innermost. Передаются в `DependencyInjector(layers=...)`.

Файл намеренно зависит только от archtool: его импортирует
`web_fractal.building_utils` на этапе загрузки, поэтому здесь не должно быть
тяжёлых/циклических импортов.
"""
from archtool.global_types import AppModule
from archtool.layers.default_layers import (
    ApplicationLayer,
    DomainLayer,
    InfrastructureLayer,
    PresentationLayer,
)

# Bounded contexts. Порядок не важен — archtool строит граф зависимостей сам.
APPS: list[AppModule] = [
    AppModule("app.users"),
    AppModule("app.todos"),
]

# Все 4 дефолтных слоя. Список (не frozenset) — порядок итерации стабилен.
# Infrastructure → Domain → Application → Presentation (внутренний слой не знает о внешнем).
app_layers: list[type] = [
    PresentationLayer,
    ApplicationLayer,
    DomainLayer,
    InfrastructureLayer,
]
