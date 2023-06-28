from common_in_tests import *


logger.set_level('WARNING')

if __name__ == '__main__':
    use_gui = False
    swith_on_exceptions()
    controller, app, mainScreen = get_controller(use_gui=use_gui)
    if use_gui:
        mainScreen.show()

    # First turn
    for i in [1, 2, 3, 4, 5]:
        controller.process_action(ACTION_LOCATION + f"_{i}")
    controller.process_action(ACTION_NEXT)
    # Lord turn
    controller.players[1].tickets = [Card("1_0"), Card("1_1")]
    logger.warning("Lord with 2 ticket takes tickets and must discard ticket 2 times")
    controller.process_action(ACTION_TAKE_TICKET)
    check_sets(set([ACTION_DISCARD_TICKET + "_" + str(i) for i in range(4)]), set(controller.possible_actions))
    controller.process_action(ACTION_DISCARD_TICKET + "_3")
    check_sets(set([ACTION_DISCARD_TICKET + "_" + str(i) for i in range(3)]), set(controller.possible_actions))
    controller.process_action(ACTION_DISCARD_TICKET + "_1")
    check_sets({ACTION_NEXT}, set(controller.possible_actions))
    logger.warning("'Discard ticket' test is successfully passed!")

    if use_gui:
        app.exec()
