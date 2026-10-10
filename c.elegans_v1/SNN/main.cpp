#include "Brain.h"
#include <iostream>
#include <thread> // Gecikme (animasyon) için
#include <chrono>

int main()
{
    std::cout << "Anakart uretiliyor, baglantilar lehimleniyor...\n";
    Brain brain;
    std::cout << "Sistem hazir.\n\n";

    float sensor_input[4] = {0.0f, 0.0f, 0.0f, 0.0f};
    bool command_output[4] = {false, false, false, false};

    std::cout << "=== SNN KURU TEST (DRY RUN) BASLIYOR ===\n\n";

    for (int tick = 1; tick <= 20; tick++)
    {
        if (tick == 3)
        {
            std::cout << ">>> DIS DUNYADAN ASIL (Sol Koku) SENSORUNE 2.0V ENJEKTE EDILDI! <<<\n";
            sensor_input[0] = 2.0f; // ASIL sensörüne akım ver
        }
        else
        {
            sensor_input[0] = 0.0f;
        }

        brain.tick(sensor_input, 4, command_output, 4);

        brain.print_network_activity(tick);

        if (command_output[0])
            std::cout << ">>> MOTOR TEPKISI: YUKARI (AVB) KASILDI! <<<\n";
        if (command_output[1])
            std::cout << ">>> MOTOR TEPKISI: ASAGI (AVA) KASILDI! <<<\n";
        if (command_output[2])
            std::cout << ">>> MOTOR TEPKISI: SOLA DON (RIML) KASILDI! <<<\n";
        if (command_output[3])
            std::cout << ">>> MOTOR TEPKISI: SAGA DON (RIMR) KASILDI! <<<\n";

        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    }

    std::cout << "\nTest basariyla tamamlandi.\n";
    std::cout << "total neuron: " << brain.total_nodes;
    return 0;
}