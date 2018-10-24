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


planetas_naves=[]

game = hlt.Game("Settler V16")
game_map=0

team_ships=[]

def funcion_relevancia(nave,planeta):
    numero_naves_puerto=1
    for p in planetas_naves:
        if p.id==planeta.id:
            numero_naves_puerto+=1
    distancia=nave.calculate_distance_between(planeta)

    tiempo=distancia/7+12/numero_naves_puerto

    return tiempo

def funcion_relevancia_naves(nave,enemigo):
    cantidad_total=1
    for pj in game_map.all_players():
        if enemigo in pj.all_ships():
            cantidad_total=len(pj.all_ships())
            break
    distancia=nave.calculate_distance_between(enemigo)
    return (1/cantidad_total)*distancia

def es_mio(planeta,mios):
    return (planeta.is_owned()) and (planeta.all_docked_ships()[0] in mios) or (not planeta.is_owned())

def no_esta_lleno(planeta):
    return planetas_naves.count(planeta)+len(planeta.all_docked_ships())<planeta.num_docking_spots
    
# GAME START
# Here we define the bot's name as Settler and initialize the game, including communication with the Halite engine.

# Then we print our start message to the logs
logging.info("Starting my Settler bot!")


full_attack_mode=False


while True:
    # TURN START
    # Update the map for the new turn and get the latest version
    game_map = game.update_map()

    planetas_naves=[]

    team_ships = game_map.get_me().all_ships()

    full_attack_mode=True
    for pj in game_map.all_players():
        if pj.id!=game_map.get_me().id:
            if 2*len(pj.all_ships())>len(team_ships):
                full_attack_mode=False
                break


    # Here we define the set of commands to be sent to the Halite engine at the end of the turn
    command_queue = []
    # For every ship that I control
    for ship in team_ships:
        # If the ship is docked
        if ship.docking_status != ship.DockingStatus.UNDOCKED:
            # Skip this ship
            continue

        diccionario={}
        for p in game_map.all_planets():
            diccionario[funcion_relevancia(ship,p)]=p

        ordDict = OrderedDict(sorted(diccionario.items(), key=lambda t: t[0]))

        planetas_factibles=[ordDict[tiempo] for tiempo in ordDict if es_mio(ordDict[tiempo],team_ships) and no_esta_lleno(ordDict[tiempo]) and not ordDict[tiempo].is_full()]

        for nave in game_map._all_ships():
            if nave not in team_ships:        
                diccionario[funcion_relevancia_naves(ship,nave)*10]=nave

        ordDict = OrderedDict(sorted(diccionario.items(), key=lambda t: t[0]))

        naves_atacar=[ordDict[coeficiente] for coeficiente in ordDict]

        cercanos=game_map.nearby_entities_by_distance(ship)
        cercanos = OrderedDict(sorted(cercanos.items(), key=lambda t: t[0]))
        closest_enemy_ships = [cercanos[distance][0] for distance in cercanos if isinstance(cercanos[distance][0], hlt.entity.Ship) and cercanos[distance][0] not in team_ships]
        planetas_cercanos=[cercanos[distance][0] for distance in cercanos if isinstance(cercanos[distance][0],hlt.entity.Planet) and (cercanos[distance][0].all_docked_ships() in team_ships and not cercanos[distance][0].is_full() or not cercanos[distance][0].is_owned())]

        if full_attack_mode==False:
            if len(planetas_factibles)>0 and (ship.calculate_distance_between(planetas_factibles[0])<ship.calculate_distance_between(closest_enemy_ships[0])):
                target_planet=planetas_factibles[0]
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
                        planetas_naves.append(target_planet)                
            else:
                target_ship=closest_enemy_ships[0]
                navigate_command = ship.navigate(
                                ship.closest_point_to(target_ship),
                                game_map,
                                speed=int(hlt.constants.MAX_SPEED),
                                ignore_ships=False)

                if navigate_command:
                        command_queue.append(navigate_command)
        else:
            if len(planetas_cercanos)>0:
                target_planet=planetas_cercanos[0]
                if ship.calculate_distance_between(planetas_cercanos[0])-planetas_cercanos[0].radius<7:
                    if ship.can_dock(target_planet):
                        command_queue.append(ship.dock(target_planet))
                    else:
                        navigate_command = ship.navigate(
                                ship.closest_point_to(target_planet),
                                game_map,
                                speed=int(hlt.constants.MAX_SPEED),
                                ignore_ships=True)

                        if navigate_command:
                            command_queue.append(navigate_command)
                else:
                    target_ship=closest_enemy_ships[0]
                    navigate_command = ship.navigate(
                                    ship.closest_point_to(target_ship),
                                    game_map,
                                    speed=int(hlt.constants.MAX_SPEED),
                                    ignore_ships=False)

                    if navigate_command:
                            command_queue.append(navigate_command)
            else:
                    target_ship=closest_enemy_ships[0]
                    navigate_command = ship.navigate(
                                    ship.closest_point_to(target_ship),
                                    game_map,
                                    speed=int(hlt.constants.MAX_SPEED),
                                    ignore_ships=False)

                    if navigate_command:
                            command_queue.append(navigate_command)
    # Send our set of commands to the Halite engine for this turn
    game.send_command_queue(command_queue)
    # TURN END
# GAME END
