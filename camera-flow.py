import cv2
import time
import os
import uuid

# Configurações
class_name = 'sprite_lata_350'  # Nome para classificar o tipo de fotos
output_dir = f'data/images-04-06/{class_name}'
capture_interval = 8  # Intervalo em segundos
total_photos = 20  # Quantidade total de fotos a serem tiradas
indicator_duration = 1.5  # Duração do indicador visual em segundos

# Criar pasta de saída se não existir
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

print("Ligando camera 0")
camera = cv2.VideoCapture(0)
print("Camera 0 ligada")

photos_taken = 0
start_time = time.time()
countdown_time = 5  # Tempo para contagem regressiva
next_capture_time = start_time + capture_interval
show_indicator = False
indicator_start_time = 0

while photos_taken < total_photos:
    _ , frame = camera.read()
    if frame is None or frame.size == 0:
        continue

    current_time = time.time()
    time_left = int(next_capture_time - current_time)

    display_frame = frame.copy()

    if show_indicator and (current_time - indicator_start_time < indicator_duration):
        text = 'FOTO TIRADA!'
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 2, 3)[0]
        text_x = (display_frame.shape[1] - text_size[0]) // 2
        text_y = (display_frame.shape[0] + text_size[1]) // 2
        cv2.putText(display_frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3, cv2.LINE_AA)
    else:
        show_indicator = False

    if time_left <= 0:
        # Gerar UUID e nome único para a foto
        unique_id = uuid.uuid4()
        photo_name = f'{class_name}_{photos_taken + 1}_{unique_id}.jpg'
        photo_path = os.path.join(output_dir, photo_name)

        # Tirar foto sem texto
        cv2.imwrite(photo_path, frame)
        photos_taken += 1

        # Resetar tempo para próxima captura
        next_capture_time = current_time + capture_interval

        # Iniciar indicador visual
        show_indicator = True
        indicator_start_time = current_time

    # Adicionar contador no frame de exibição
    if time_left <= countdown_time:
        countdown_color = (255, 255, 255) if time_left - 1 > 0 else (0, 0, 255)
        cv2.putText(display_frame, str(time_left - 1), (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 3, countdown_color, 4, cv2.LINE_AA)
    # Contagem de fotos no canto superior direito
    cv2.putText(display_frame, f'Fotos tiradas: {photos_taken}', (display_frame.shape[1] - 300, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
    cv2.imshow("Live Camera", display_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Finalizar e liberar recursos
camera.stop()
cv2.destroyAllWindows()
print(f"{photos_taken} fotos foram tiradas e salvas em '{output_dir}'")
