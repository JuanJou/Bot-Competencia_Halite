"""
Welcome to your first Halite-II bot!

This bot's name is Settler. It's purpose is simple (don't expect it to win complex games :) ):
1. Initialize game
2. If a ship is not docked and there are unowned planets
2.a. Try to Dock in the planet if close enough
2.b If not, go towards the planet

Note: Please do not place print statements here as they are used to communicate with the Halite engine. If you need
to log anything use the logging module.
"""
# Let's start by importing the Halite Starter Kit so we can interface with the Halite engine
import hlt
# Then let's import the logging module so we can print out information
import logging

from collections import OrderedDict

# GAME START
# Here we define the bot's name as Settler and initialize the game, including communication with the Halite engine.
game = hlt.Game("Settler Bis")
# Then we print our start message to the logs
logging.info("Starting my Settler bot!")

contador=0

    


while True:
    # TURN START
    # Update the map for the new turn and get the latest version
    game_map = game.update_map()

    atacar=0

    # Here we define the set of commands to be sent to the Halite engine at the end of the turn
    command_queue = []
    # For every ship that I control
    for ship in game_map.get_me().all_ships():
        # If the ship is docked
        if ship.docking_status != ship.DockingStatus.UNDOCKED:
            # Skip this ship
            continue

        cercanos=game_map.nearby_entities_by_distance(ship)
        cercanos = OrderedDict(sorted(cercanos.items(), key=lambda t: t[0]))

        closest_empty_planets = [cercanos[distance][0] for distance in cercanos if isinstance(cercanos[distance][0], hlt.entity.Planet) and not cercanos[distance][0].is_owned()]

        if contador%10==0:
            disparar=atacar%4==0

        team_ships = game_map.get_me().all_ships()
        closest_enemy_ships = [cercanos[distance][0] for distance in cercanos if isinstance(cercanos[distance][0], hlt.entity.Ship) and cercanos[distance][0] not in team_ships]
        # For each planet in the game (only non-destroyed planets are included)
        if len(closest_empty_planets) > 0 and disparar==False:
            target_planet = closest_empty_planets[0]
            if ship.can_dock(target_planet):
                command_queue.append(ship.dock(target_planet))
            else:
                navigate_command = ship.navigate(
                            ship.closest_point_to(target_planet),
                            game_map,
                            speed=int(hlt.constants.MAX_SPEED),
                            ignore_ships=False)

                if navigate_command:
                    command_queue.append(navigate_command) 

        # FIND SHIP TO ATTACK!
        elif len(closest_enemy_ships) > 0:
            atacando=True
            target_ship = closest_enemy_ships[0]
            navigate_command = ship.navigate(
                        ship.closest_point_to(target_ship),
                        game_map,
                        speed=int(hlt.constants.MAX_SPEED),
                        ignore_ships=False)

            if navigate_command:
                command_queue.append(navigate_command)
        atacar=atacar+1

    contador=contador+1
    # Send our set of commands to the Halite engine for this turn
    game.send_command_queue(command_queue)
    # TURN END
# GAME END
