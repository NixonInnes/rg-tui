from rg_tui.app import RgTui


def rg_tui():
    app = RgTui()
    app.run()


def rg_tui_inline():
    app = RgTui()
    app.run(inline=True)
