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


def owned_by_us(planeta,mios):
    anclados=planeta.all_docked_ships()
    for ship in anclados:
        if ship in mios:
            return True
    return False


def reagrupar(nave,amigos):
    for ship in amigos:
        if ship.docking_status==ship.DockingStatus.UNDOCKED and ship.id!=nave.id:
            navigate_command = nave.navigate(
                            nave.closest_point_to(ship),
                            game_map,
                            speed=int(hlt.constants.MAX_SPEED),
                            ignore_ships=False)
            if navigate_command:
                command_queue.append(navigate_command)
                return


# GAME START
# Here we define the bot's name as Settler and initialize the game, including communication with the Halite engine.
game = hlt.Game("Settler V10")
# Then we print our start message to the logs
logging.info("Starting my Settler bot!")

contador=0

full_attack_mode=False
    


while True:
    # TURN START
    # Update the map for the new turn and get the latest version
    game_map = game.update_map()

    atacar=0


    planetas_gobernados=0
    radio_total=0

    for p in game_map.all_planets():
        for nave in p.all_docked_ships():
            if nave in game_map.get_me().all_ships():
                planetas_gobernados+=p.radius
        radio_total+=p.radius
    
    full_attack_mode=planetas_gobernados>radio_total/2

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
        disparar=atacar%4==0

        team_ships = game_map.get_me().all_ships()

        amigos = [cercanos[distance][0] for distance in cercanos if isinstance(cercanos[distance][0], hlt.entity.Ship) and cercanos[distance][0] in team_ships]

        closest_planets_owned= [cercanos[distance][0] for distance in cercanos if isinstance(cercanos[distance][0], hlt.entity.Planet) and not cercanos[distance][0].is_full() and owned_by_us(cercanos[distance][0],team_ships)]
        closest_enemy_ships = [cercanos[distance][0] for distance in cercanos if isinstance(cercanos[distance][0], hlt.entity.Ship) and cercanos[distance][0] not in team_ships]

        
        if full_attack_mode==False:
            if len(closest_empty_planets) > 0 and disparar==False:
                target_planet = closest_empty_planets[0]
                if ship.can_dock(target_planet):
                    command_queue.append(ship.dock(target_planet))
                else:
                    navigate_command = ship.navigate(
                                ship.closest_point_to(closest_enemy_ships[0]),
                                game_map,
                                speed=int(hlt.constants.MAX_SPEED),
                                ignore_ships=False)

                    if navigate_command:
                        command_queue.append(navigate_command)

            elif len(closest_enemy_ships) > 0 and ship.calculate_distance_between(closest_enemy_ships[0])<14:
                navigate_command = ship.navigate(
                            ship.closest_point_to(closest_enemy_ships[0]),
                            game_map,
                            speed=int(hlt.constants.MAX_SPEED),
                            ignore_ships=False)
                if navigate_command:
                        command_queue.append(navigate_command)    
            else:
                if len(closest_planets_owned)>0:
                    target_planet = closest_planets_owned[0]
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
                else:
                    reagrupar(ship,amigos)

            atacar=atacar+1
        else:
            if len(closest_empty_planets) > 0:
                if ship.calculate_distance_between(closest_empty_planets[0])-closest_empty_planets[0].radius<5:
                    target_planet = closest_empty_planets[0]
                    if ship.can_dock(target_planet):
                        command_queue.append(ship.dock(target_planet))
                else:
                    navigate_command = ship.navigate(
                                ship.closest_point_to(closest_enemy_ships[0]),
                                game_map,
                                speed=int(hlt.constants.MAX_SPEED),
                                ignore_ships=False)
                    if navigate_command:
                        command_queue.append(navigate_command)

    contador=contador+1
    # Send our set of commands to the Halite engine for this turn
    game.send_command_queue(command_queue)
    # TURN END
# GAME END

