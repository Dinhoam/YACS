from kivent_core.systems.gamesystem import GameSystem
from kivy.factory import Factory
from kivy.properties import NumericProperty, BooleanProperty, ObjectProperty
from kivy.clock import Clock
from kivy.vector import Vector


class PlayerSystem(GameSystem):
    current_entity = NumericProperty(None, allownone=True)
    physics_system = ObjectProperty(None)
    camera_system = ObjectProperty(None)
    touch_count = NumericProperty(0)

    def __init__(self, **kwargs):
        super(PlayerSystem, self).__init__(**kwargs)

    def set_boosting(self, dt):
        if self.current_entity is not None:
            entity = self.gameworld.entities[self.current_entity]
            ship_comp = entity.ship_system
            ship_comp.boosting = True

    def get_distance_from_player_scalar(self, position, max_distance=250):
        current_entity = self.current_entity
        entities = self.gameworld.entities
        if current_entity == None:
            return 0.

        entity = entities[current_entity]
        position_comp = entity.position
        distance = Vector(position_comp.pos).distance(position)
        if distance > max_distance:
            return 0.
        else:
            return 1. - distance/max_distance

    def on_touch_down(self, touch):
        self.touch_count += 1
        touch_radius = 20
        touch_count = self.touch_count
        physics_system = self.physics_system
        camera_system = self.camera_system
        world_pos = camera_system.convert_from_screen_to_world(touch.pos)
        x, y = world_pos
        collide_area = [
            x - touch_radius, y - touch_radius,
            x + touch_radius, y + touch_radius
            ]
        if self.current_entity is not None:
            entity = self.gameworld.entities[self.current_entity]
            collisions = physics_system.query_bb(collide_area)
            if len(collisions) > 0:
                weapons = entity.projectile_weapons
                weapons.firing = True
            elif touch_count == 1:
                steering = entity.steering
                steering.target = world_pos
                steering.active = True
                Clock.schedule_once(self.set_boosting, .5)
            elif touch_count == 2:
                weapons = entity.projectile_weapons
                weapons.firing = True
                Clock.unschedule(self.set_boosting)
        super(PlayerSystem, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.current_entity is not None:
            entity = self.gameworld.entities[self.current_entity]
            ship_comp = entity.ship_system
            ship_comp.boosting = False
        Clock.unschedule(self.set_boosting)
        self.touch_count -= 1
        super(PlayerSystem, self).on_touch_up(touch)

    def load_player(self):
        ship_system = self.gameworld.system_manager['ship_system']
        ship_id = ship_system.load_ship('ship1', True, (500., 500.))
        self.current_entity = ship_id
        entity = self.gameworld.entities[ship_id]
        emitters = entity.emitters
        emitter = emitters.emitters[0]
        emitter.emit_angle_offset = 180.
        emitter.pos_offset = (50., 0.)
        camera = self.gameworld.system_manager['camera_planet2']
        camera.focus_entity = True
        camera.entity_to_focus = ship_id

Factory.register('PlayerSystem', cls=PlayerSystem)