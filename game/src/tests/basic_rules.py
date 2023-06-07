from common_in_tests import *


if __name__ == '__main__':
    swith_on_exceptions()
    use_gui = True
    controller, app, mainScreen = get_controller(use_gui=use_gui)
    if use_gui:
        mainScreen.show()

    # create test decks
    controller.state.event_deck.cards = ["MONEY_TRAIL", "DARKESS_RETURNS", "LUCY_REVENGE", "ENRAGED", "PLANNED_AMBUSH",
                                         "DEVILISH_POWER"]
    controller.state.tickets_deck.cards = ["3_2", "2_2", "1_0", "3_2", "3_2"]
    controller.state.item_deck.cards = ["CRUCIFIX", "GARLIC", "PISTOL", "RIFLE", "HOLY_BULLETS"]

    loc_dict = Loader.location_dict
    start_loc = set(["ActionLocation_" + str(loc) for loc in loc_dict.keys() if not loc_dict[loc]['isSea']])
    start_loc.remove("ActionLocation_" + SpecificLocations.DRACULA_CASTLE.value)

    #Cologne, Salonica, Sarajevo, Belgrade, Geneva
    for i in [27, 47, 50, 5, 22]:
        name = Loader.num_to_player(controller.state.who_moves)
        check_sets(start_loc, set(controller.possible_actions))
        action = ACTION_LOCATION + f"_{i}"
        controller.process_action(action)
        start_loc.remove(action)

    controller.process_action(ACTION_NEXT)

    logger.info("Lord takes ticket at Day")
    actions = {ACTION_NEXT, ACTION_MOVE_BY_ROAD, ACTION_TAKE_TICKET, ACTION_SUPPLY}
    check_sets(actions, set(controller.possible_actions))
    controller.process_action(ACTION_TAKE_TICKET)  # take "3_2", "2_2"
    controller.process_action(ACTION_NEXT)

    logger.info("Doctor takes ticket at Day")
    actions = {ACTION_NEXT, ACTION_MOVE_BY_ROAD, ACTION_TAKE_TICKET, ACTION_SUPPLY, ACTION_MOVE_BY_SEA}
    check_sets(actions, set(controller.possible_actions))
    controller.process_action(ACTION_TAKE_TICKET)  # take "1_0"
    controller.process_action(ACTION_NEXT)

    logger.info("Helsing move by road at Day")
    actions = {ACTION_NEXT, ACTION_MOVE_BY_ROAD, ACTION_TAKE_TICKET, ACTION_SUPPLY}
    check_sets(actions, set(controller.possible_actions))
    controller.process_action(ACTION_MOVE_BY_ROAD)
    actions = {'ActionLocation_5', 'ActionLocation_11', 'ActionLocation_23', 'ActionLocation_52'}
    check_sets(actions, set(controller.possible_actions))
    controller.process_action('ActionLocation_23')
    controller.process_action(ACTION_NEXT)

    logger.info("Mina supply at Day at village")
    actions = {ACTION_NEXT, ACTION_MOVE_BY_ROAD, ACTION_TAKE_TICKET, ACTION_SUPPLY}
    check_sets(actions, set(controller.possible_actions))
    controller.process_action(ACTION_SUPPLY)
    check_sets({"MONEY_TRAIL"}, set(controller.players[4].events))
    check_sets(set(), set(controller.players[4].items))
    controller.process_action(ACTION_NEXT)

    logger.info("Lord supply at Night")
    actions = {ACTION_NEXT, ACTION_TAKE_TICKET, ACTION_SUPPLY}
    check_sets(actions, set(controller.possible_actions))
    controller.process_action(ACTION_SUPPLY)
    check_sets({"DEVILISH_POWER"}, set(controller.players[0].events))
    check_sets({"CRUCIFIX", "GARLIC"}, set(controller.players[1].items))
    controller.process_action(ACTION_NEXT)

    logger.info("Doctor supply at Night")
    actions = {ACTION_NEXT, ACTION_TAKE_TICKET, ACTION_SUPPLY}
    check_sets(actions, set(controller.possible_actions))
    controller.process_action(ACTION_SUPPLY)
    check_sets({"PLANNED_AMBUSH"}, set(controller.players[2].events))
    check_sets(set(), set(controller.players[2].items))
    controller.process_action(ACTION_NEXT)

    logger.info("Helsing skip turn")
    actions = {ACTION_NEXT, ACTION_TAKE_TICKET, ACTION_SUPPLY}
    check_sets(actions, set(controller.possible_actions))
    controller.process_action(ACTION_NEXT)

    logger.info("Mina skip turn")
    actions = {ACTION_NEXT, ACTION_TAKE_TICKET, ACTION_SUPPLY}
    check_sets(actions, set(controller.possible_actions))
    controller.process_action(ACTION_NEXT)

    logger.info("Dracula moves to Paris (43)")
    actions = {ACTION_MOVE_BY_ROAD}
    check_sets(actions, set(controller.possible_actions))
    controller.process_action(ACTION_MOVE_BY_ROAD)
    actions = {'ActionLocation_29', 'ActionLocation_37', 'ActionLocation_43', 'ActionLocation_53',
                        'ActionLocation_58'}
    check_sets(actions, set(controller.possible_actions))
    controller.process_action('ActionLocation_43')
    controller.process_action(ACTION_NEXT)

    logger.info("Lord use ticket at Day and move to Berlin (6)")
    actions = {ACTION_NEXT, ACTION_MOVE_BY_ROAD, ACTION_TAKE_TICKET, ACTION_SUPPLY, ACTION_MOVE_BY_RAILWAY}
    check_sets(actions, set(controller.possible_actions))
    controller.process_action(ACTION_MOVE_BY_RAILWAY)
    actions = {'ActionLocation_6', 'ActionLocation_8', 'ActionLocation_57', 'ActionLocation_17', 'ActionLocation_31',
               'ActionLocation_45', 'ActionLocation_43', 'ActionLocation_53', 'ActionLocation_42', 'ActionLocation_7',
               'ActionLocation_15', 'ActionLocation_37', 'ActionLocation_39', 'ActionLocation_58', 'Ticket_2'}
    check_sets(actions, set(controller.possible_actions))
    controller.process_action('Ticket_2')
    actions = {'ActionLocation_6', 'ActionLocation_8', 'ActionLocation_57', 'ActionLocation_17', 'ActionLocation_31',
               'ActionLocation_45', 'ActionLocation_43', 'ActionLocation_53', 'Ticket_1'}
    check_sets(actions, set(controller.possible_actions))
    controller.process_action('ActionLocation_6')
    controller.process_action(ACTION_NEXT)

    logger.info("Doctor has ticket, but cannot move by railway. He moves to Ionic sea")
    actions = {ACTION_NEXT, ACTION_MOVE_BY_SEA, ACTION_MOVE_BY_ROAD, ACTION_TAKE_TICKET, ACTION_SUPPLY}
    check_sets(actions, set(controller.possible_actions))
    controller.process_action(ACTION_MOVE_BY_SEA)
    check_sets({'ActionLocation_64'}, set(controller.possible_actions))
    controller.process_action('ActionLocation_64')
    controller.process_action(ACTION_NEXT)

    logger.info("Helsing and Mina skip Day turns")
    for i in range(2):
        actions = {ACTION_NEXT, ACTION_MOVE_BY_ROAD, ACTION_TAKE_TICKET, ACTION_SUPPLY}
        check_sets(actions, set(controller.possible_actions))
        controller.process_action(ACTION_NEXT)

    logger.info("Lord skips Night turn")
    actions = {ACTION_NEXT, ACTION_TAKE_TICKET, ACTION_SUPPLY}
    check_sets(actions, set(controller.possible_actions))
    controller.process_action(ACTION_NEXT)

    logger.info("Doctor on sea at Night")
    actions = {ACTION_NEXT}
    check_sets(actions, set(controller.possible_actions))
    controller.process_action(ACTION_NEXT)

    check_lists(["DARKESS_RETURNS", "LUCY_REVENGE", "ENRAGED"], controller.state.event_deck.cards)
    check_lists(["3_2", "3_2"], controller.state.tickets_deck.cards)
    check_lists(["2_2"], controller.state.tickets_deck.discard_pile)
    check_lists(["PISTOL", "RIFLE", "HOLY_BULLETS"], controller.state.item_deck.cards)

    logger.info("Take item, events, move by road, move by sea, move by railway is successfully tested!")
    if use_gui:
        app.exec()