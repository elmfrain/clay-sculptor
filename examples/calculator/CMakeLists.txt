cmake_minimum_required(VERSION 3.20)

project(calculator)

add_executable(${PROJECT_NAME}
    main.c
)

clay_sculptor_add_ui(TARGET ${PROJECT_NAME}
    ui/calculator.ui
)

clay_sculptor_add_style(TARGET ${PROJECT_NAME}
    style/main.style
)
