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

planetas_a_ocupar=[]

turno=1
planeta=0
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

def alguno_cerca(nave,planetas):
    for p in planetas:
        if nave.calculate_distance_between(p)>30:
            return False
        elif ship.can_dock(p):
            return True

def no_ser_ocupado(planeta,amigos):
    for p,s in planetas_a_ocupar:
        if p.id==planeta.id:
            if s in amigos:
                return False
            else:
                return True
    return True

def extraer_planeta(target):
    for p,s in planetas_a_ocupar:
        if p.id==target.id:
            planetas_a_ocupar.remove(p,s)

def insertar_solo(planeta,ship):
    if (planeta,ship) not in planetas_a_ocupar:
        planetas_a_ocupar.append(planeta,ship)
# GAME START
# Here we define the bot's name as Settler and initialize the game, including communication with the Halite engine.
game = hlt.Game("Settler V12")
# Then we print our start message to the logs
logging.info("Starting my Settler bot!")

contador=0

full_attack_mode=False
    


while True:
    # TURN START
    # Update the map for the new turn and get the latest version
    game_map = game.update_map()


    planetas_a_ocupar=[]

    team_ships = game_map.get_me().all_ships()

    planetas_gobernados=0
    radio_total=0

    radio_otros_jugadores=[]

    radio=0

    for j in game_map.all_players():
        if j.id!=game_map.get_me().id:
            for p in game_map.all_planets():
                if p.is_owned() and p.all_docked_ships() in j.all_ships():
                    radio=radio+p.radius
            radio_otros_jugadores.append(radio)
            radio=0
        else:
             for p in game_map.all_planets():
                if p.is_owned() and p.all_docked_ships() in game_map.get_me().all_ships():
                    radio_total=radio_total+p.radius
    
    for x in radio_otros_jugadores:
        if x>radio_total:
            full_attack_mode=False
            break
        else:
            full_attack_mode=True

    if full_attack_mode:
        for ship in team_ships:
            ship.full_attack=True

    # Here we define the set of commands to be sent to the Halite engine at the end of the turn
    command_queue = []

    # For every ship that I control
    for ship in team_ships:
        # If the ship is docked
        if ship.docking_status != ship.DockingStatus.UNDOCKED:
            # Skip this ship
            continue

        cercanos=game_map.nearby_entities_by_distance(ship)
        cercanos = OrderedDict(sorted(cercanos.items(), key=lambda t: t[0]))

        closest_empty_planets = [cercanos[distance][0] for distance in cercanos if isinstance(cercanos[distance][0], hlt.entity.Planet) and not cercanos[distance][0].is_owned()]     
        amigos = [cercanos[distance][0] for distance in cercanos if isinstance(cercanos[distance][0], hlt.entity.Ship) and cercanos[distance][0] in team_ships]
        closest_planets_owned= [cercanos[distance][0] for distance in cercanos if isinstance(cercanos[distance][0], hlt.entity.Planet) and not cercanos[distance][0].is_full() and owned_by_us(cercanos[distance][0],team_ships)]
        closest_enemy_ships = [cercanos[distance][0] for distance in cercanos if isinstance(cercanos[distance][0], hlt.entity.Ship) and cercanos[distance][0] not in team_ships]

        #ORDENAR POR COEFICIENTE RECORRIDO/RADIO

        if turno==1:
            navigate_command = ship.navigate(
                                    ship.closest_point_to(closest_empty_planets[planeta*2]),
                                    game_map,
                                    speed=int(hlt.constants.MAX_SPEED),
                                    ignore_ships=False)
            if navigate_command:
                command_queue.append(navigate_command)
            planeta+=1
            turno+=1
            break
        
        if ship.full_attack==False:
            if len(closest_empty_planets) > 0 and ship.calculate_distance_between(closest_enemy_ships[0])>20:
                    for target_planet in closest_empty_planets:
                        if no_ser_ocupado(target_planet,team_ships):
                            if ship.can_dock(target_planet):
                                command_queue.append(ship.dock(target_planet))
                                extraer_planeta(target_planet)
                            else:
                                navigate_command = ship.navigate(
                                    ship.closest_point_to(target_planet),
                                    game_map,
                                    speed=int(hlt.constants.MAX_SPEED),
                                    ignore_ships=False)
                                insertar_solo(target_planet,ship)
                                if navigate_command:
                                    command_queue.append(navigate_command)
                            break
            elif len(closest_enemy_ships) > 0 and ship.calculate_distance_between(closest_enemy_ships[0])<14:
                navigate_command = ship.navigate(
                            ship.closest_point_to(closest_enemy_ships[0]),
                            game_map,
                            speed=int(hlt.constants.MAX_SPEED),
                            ignore_ships=False)
                if navigate_command:
                        command_queue.append(navigate_command)    
            else:
                if len(closest_planets_owned)>0 and ship.calculate_distance_between(closest_planets_owned[0])<25:
                    for target_planet in closest_planets_owned:
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

                else:
                    if ship.calculate_distance_between(amigos[0])>3:
                        reagrupar(ship,amigos)
                    else:
                        ship.full_attack=True
        else:
            if len(closest_empty_planets) > 0:
                if ship.calculate_distance_between(closest_empty_planets[0])-closest_empty_planets[0].radius<5:
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
                else:
                    navigate_command = ship.navigate(
                                ship.closest_point_to(closest_enemy_ships[0]),
                                game_map,
                                speed=int(hlt.constants.MAX_SPEED),
                                ignore_ships=False)
                    if navigate_command:
                        command_queue.append(navigate_command)
            else:
                    navigate_command = ship.navigate(
                                ship.closest_point_to(closest_enemy_ships[0]),
                                game_map,
                                speed=int(hlt.constants.MAX_SPEED),
                                ignore_ships=False)
                    if navigate_command:
                        command_queue.append(navigate_command)

    # Send our set of commands to the Halite engine for this turn
    game.send_command_queue(command_queue)
    # TURN END
# GAME END

