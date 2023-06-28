from common_in_tests import *


logger.set_level('WARNING')

if __name__ == '__main__':

    use_gui = False
    swith_on_exceptions()
    controller, app, mainScreen = get_controller(use_gui=use_gui)
    if use_gui:
        mainScreen.show()

     #First turn
    for i in [1, 2, 3, 4, 5]:
        controller.process_action(ACTION_LOCATION + f"_{i}")
    controller.process_action(ACTION_NEXT)
    #Lord turn
    controller.state.event_deck.cards[-1] = "ROADBLOCK"

    controller.players[2].items = [Card("KNIFE"), Card("RIFLE"), Card("PISTOL")]
    controller.players[2].events = [Card("LUCY_REVENGE"), Card("MONEY_TRAIL"), Card("PLANNED_AMBUSH")]
    controller.players[0].events = [Card("CUSTOMS_SEARCH"), Card("DARKESS_RETURNS"), Card("DEVILISH_POWER"),
                                    Card('ENRAGED')]
    controller.players[2].tickets = [Card("2_2"), Card("1_1")]
    for i in range(4):
        controller.process_action(ACTION_NEXT)

    logger.warning("Lord draw event at night and it is 5th Dracula event, which later must to discard immediately")

    logger.info(f"event_deck : {controller.state.event_deck.cards}")
    controller.get_current_player().supply(controller.state, controller.possible_actions, controller.players)
    check_who_moves(DRACULA, controller.state.who_moves)
    check_sets(set([ACTION_DISCARD_EVENT + "_" + str(i) for i in range(5)]), set(controller.possible_actions))
    controller.process_action(ACTION_DISCARD_EVENT + "_4")
    check_who_moves(LORD, controller.state.who_moves)
    check_sets({ACTION_NEXT}, set(controller.possible_actions))

    logger.warning("'Discard 5th Dracula event during Hunter turn' test is successfully passed!")

    if use_gui:
        app.exec()
