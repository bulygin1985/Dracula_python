from common_in_tests import *


logger.set_level('WARNING')

if __name__ == '__main__':

    Param.use_lair = True

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

    for i in range(9):
        controller.process_action(ACTION_NEXT)
    logger.warning("Dracula moves from Brussels to Cologne and meet Lord")
    controller.process_action(ACTION_LOCATION + f"_{27}")
    check_sets({ACTION_NEXT}, set(controller.possible_actions))
    logger.warning("Dracula track:")
    for i, hideout in enumerate(dracula.track):
        logger.warning(f"{i} : {hideout}")

    controller.process_action(ACTION_NEXT)
    # Here is day COMBAT between Lord and Dracula
    logger.warning("Lord moves from Cologne to Frankfurt")
    controller.process_action(ACTION_LOCATION + f"_{57}")
    for i in range(8):
        controller.process_action(ACTION_NEXT)
    logger.warning("Dracula moves from Cologne to Strasbourg")
    controller.process_action(ACTION_LOCATION + f"_{53}")
    check_sets({ACTION_CHOOSE_ENCOUNTER}, set(controller.possible_actions))
    controller.process_action(ACTION_CHOOSE_ENCOUNTER + "_2")
    check_lists(["UNNATURAL_FOG"] + 2 * ["SPY"], controller.state.encounter_deck.cards)
    check_lists(["RATS"] + ["SZGANY_BODYGUARDS"] + 2 * ["SZGANY_MOB"] + ["UNNATURAL_FOG"], dracula.encounters)
    check_sets({"WOLVES"}, {dracula.track[0].encounters[0].__class__.__name__})

    logger.warning("Dracula track:")
    for i, hideout in enumerate(dracula.track):
        logger.warning(f"{i} : {hideout}")

    check_sets({ACTION_NEXT}, set(controller.possible_actions))
    controller.process_action(ACTION_NEXT)
    for i in range(8):
        controller.process_action(ACTION_NEXT)
    logger.warning("Dracula moves from Strasbourg to Zurich")
    controller.process_action(ACTION_LOCATION + f"_{58}")
    check_sets({ACTION_CHOOSE_ENCOUNTER}, set(controller.possible_actions))
    controller.process_action(ACTION_CHOOSE_ENCOUNTER + "_0")
    check_lists(2 * ["SPY"], controller.state.encounter_deck.cards)
    check_lists(["SZGANY_BODYGUARDS"] + 2 * ["SZGANY_MOB"] + 2 * ["UNNATURAL_FOG"], dracula.encounters)
    check_sets({ACTION_NEXT}, set(controller.possible_actions))
    logger.warning("Dracula track:")
    for i, hideout in enumerate(dracula.track):
        logger.warning(f"{i} : {hideout}")
    controller.process_action(ACTION_NEXT)

    logger.warning("Lord moves from Strasbourg with Dracula encounter")
    controller.process_action(ACTION_LOCATION + f"_{53}")
    logger.warning("Dracula chooses to do not ambush")
    check_lists([DRACULA], [controller.state.who_moves])
    check_sets({ACTION_IS_AMBUSHED}, set(controller.possible_actions))
    controller.process_action(ACTION_IS_AMBUSHED + f"_{0}")
    check_lists([LORD], [controller.state.who_moves])
    check_sets({ACTION_NEXT}, set(controller.possible_actions))

    for i in range(8):
        controller.process_action(ACTION_NEXT)

    logger.warning("Dracula moves from Zurich to Milan and put Geneva to Lairs")
    controller.process_action(ACTION_LOCATION + f"_{22}")
    check_sets({ACTION_CHOOSE_ENCOUNTER}, set(controller.possible_actions))
    controller.process_action(ACTION_CHOOSE_ENCOUNTER + "_0")
    check_lists(["SPY"], controller.state.encounter_deck.cards)
    check_lists(2 * ["SZGANY_MOB"] + 2 * ["UNNATURAL_FOG"] + ["SPY"], dracula.encounters)
    check_sets({ACTION_IS_PUT_TO_LAIR}, set(controller.possible_actions))
    controller.process_action(ACTION_IS_PUT_TO_LAIR + "_1")
    check_sets({ACTION_CHOOSE_LAIR_ENCOUNTER}, set(controller.possible_actions))
    controller.process_action(ACTION_CHOOSE_LAIR_ENCOUNTER + "_0")
    check_sets({"SZGANY_MOB"}, {dracula.lairs[0].encounters[0].__class__.__name__})
    print(controller.possible_actions)

    logger.warning("Dracula track:")
    for i, hideout in enumerate(dracula.track):
        logger.warning(f"{i} : {hideout}")

    logger.warning("Dracula Lairs:")
    for i, hideout in enumerate(dracula.lairs):
        logger.warning(f"{i} : {hideout}")

    # TODO : 1) check encounter maturing and 2) several encounter maturing (just add new encounter) 3) add 2nd encounter to lair

    if use_gui:
        app.exec()
