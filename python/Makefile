.PHONY: run

run: compile_ui
	@echo Makefile: Running...
	@echo ===============================
	@start.bat

compile_ui: compile_ui.bat typingwidget.ui resources/typingwidget.qrc
	@echo Makefile: Compiling UI files...
	@compile_ui.bat