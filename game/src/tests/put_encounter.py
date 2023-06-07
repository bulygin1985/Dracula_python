from common_in_tests import *


if __name__ == '__main__':
    swith_on_exceptions()
    use_gui = True
    controller, app, mainScreen = get_controller(use_gui=use_gui)
    if use_gui:
        mainScreen.show()

    #Cologne, Salonica, Sarajevo, Belgrade, Geneva
    for i in [27, 47, 50, 5, 22]:
        name = Loader.num_to_player(controller.state.who_moves)
        action = ACTION_LOCATION + f"_{i}"
        controller.process_action(action)

    if use_gui:
        app.exec()
