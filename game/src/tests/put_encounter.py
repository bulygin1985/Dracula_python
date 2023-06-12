from common_in_tests import *


if __name__ == '__main__':
    logger.set_level('WARNING')
    swith_on_exceptions()
    use_gui = False
    controller, app, mainScreen = get_controller(use_gui=use_gui)
    if use_gui:
        mainScreen.show()

    dracula = controller.players[0]
    dracula.encounters = 2 * ["RATS"] + 2 * ["SZGANY_BODYGUARDS"] + ["WOLVES"]
    controller.state.encounter_deck.cards = 2 * ["SZGANY_MOB"] + 2 * ["UNNATURAL_FOG"] + 2 * ["SPY"]
    #Cologne, Salonica, Sarajevo, Belgrade, Geneva
    for i in [27, 47, 50, 5, 22]:
        name = Loader.num_to_player(controller.state.who_moves)
        action = ACTION_LOCATION + f"_{i}"
        controller.process_action(action)

    for i in range(9):
        controller.process_action(ACTION_NEXT)
    logger.warning("Dracula moves from Geneva to Paris")
    controller.process_action(ACTION_LOCATION + f"_{43}")
    check_sets({ACTION_CHOOSE_ENCOUNTER}, set(controller.possible_actions))
    logger.warning(f"deck before draw: {controller.state.encounter_deck.cards}")
    controller.process_action(ACTION_CHOOSE_ENCOUNTER + "_0")
    logger.warning(f"deck after draw: {controller.state.encounter_deck.cards}")
    check_lists(["SZGANY_MOB"] + 2 * ["UNNATURAL_FOG"] + 2 * ["SPY"], controller.state.encounter_deck.cards)
    logger.warning(f"Dracula choose {dracula.encounters[0]} as encounter in Paris")
    check_sets({"RATS"}, {dracula.track[0].encounters[0].__class__.__name__})
    logger.warning(f"Dracula draw {controller.state.encounter_deck.cards[0]} from encounter deck")
    check_lists(["RATS"] + 2 * ["SZGANY_BODYGUARDS"] + ["WOLVES"] + ["SZGANY_MOB"], dracula.encounters)
    logger.warning(f"Dracula encounters : {dracula.encounters}")
    logger.warning("Dracula track:")
    for i, hideout in enumerate(dracula.track):
        logger.warning(f"{i} : {hideout}")

    for i in range(9):
        controller.process_action(ACTION_NEXT)
    logger.warning("Dracula moves from Paris to Brussels")
    controller.process_action(ACTION_LOCATION + f"_{8}")
    check_sets({ACTION_CHOOSE_ENCOUNTER}, set(controller.possible_actions))
    logger.warning(f"deck before draw: {controller.state.encounter_deck.cards}")
    controller.process_action(ACTION_CHOOSE_ENCOUNTER + "_2")
    logger.warning(f"deck after draw: {controller.state.encounter_deck.cards}")
    check_lists(2 * ["UNNATURAL_FOG"] + 2 * ["SPY"], controller.state.encounter_deck.cards)
    check_lists(["RATS"] + ["SZGANY_BODYGUARDS"] + ["WOLVES"] + 2 * ["SZGANY_MOB"], dracula.encounters)
    check_sets({"SZGANY_BODYGUARDS"}, {dracula.track[0].encounters[0].__class__.__name__})
    check_sets({"RATS"}, {dracula.track[1].encounters[0].__class__.__name__})
    logger.warning("Dracula track:")
    for i, hideout in enumerate(dracula.track):
        logger.warning(f"{i} : {hideout}")

    if use_gui:
        app.exec()
