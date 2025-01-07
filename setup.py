from cx_Freeze import setup, Executable

executables = [Executable("Munchkin.py")]

setup(
    name="Munchkin",
    version="1.0",
    description="Munchkin é um jogo de cartas humorístico que parodia aventuras de RPG de fantasia.",
    executables=executables
)
