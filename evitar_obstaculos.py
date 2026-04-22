import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

class EvitadorRoomba(Node):
    def __init__(self):
        super().__init__('evitador_roomba')
        
        # Suscripcion al sensor laser
        self.subscription = self.create_subscription(
            LaserScan, 
            '/scan', 
            self.listener_callback, 
            10)
        
        # Publicacion en el topico correcto para TurtleBot 4
        self.publisher = self.create_publisher(
            Twist, 
            '/cmd_vel_unstamped', 
            10)
        
        self.get_logger().info('Nodo estilo Roomba iniciado - Sin acentos')

    def listener_callback(self, msg):
        # El centro del array es lo que el robot tiene justo delante
        centro = len(msg.ranges) // 2
        distancia_frontal = msg.ranges[centro]
        
        move = Twist()

        # --- PARAMETROS DE CONFIGURACION ---
        UMBRAL_CHOQUE = 0.30  # Se acerca hasta 30cm de la pared
        VEL_AVANCE = 0.25     # Velocidad lineal
        VEL_GIRO = 1.0        # Giro rapido
        # -----------------------------------

        if distancia_frontal > UMBRAL_CHOQUE:
            # Avanzar recto
            move.linear.x = VEL_AVANCE
            move.angular.z = 0.0
            if distancia_frontal < 1.0:
                self.get_logger().info('Apurando pared: ' + str(round(distancia_frontal, 2)))
        else:
            # Si hay obstaculo, se detiene y gira rapido
            move.linear.x = 0.0
            move.angular.z = VEL_GIRO
            self.get_logger().info('OBSTACULO detectado. Girando...')
        
        self.publisher.publish(move)

def main(args=None):
    rclpy.init(args=args)
    nodo = EvitadorRoomba()
    
    try:
        rclpy.spin(nodo)
    except KeyboardInterrupt:
        pass
    finally:
    # Al cerrar, paramos el robot
        paro = Twist()
        nodo.publisher.publish(paro)
        nodo.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()



