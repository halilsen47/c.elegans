#include "Neuron.h"

Neuron::Neuron()
{
}

void Neuron::step()
{

    if (refractory_time > 0)
    {
        refractory_time--;
        current_volt = 0.0f;
        volt_buffer = 0.0f;
        is_fired = false;
        return;
    }

    current_volt += volt_buffer;
    volt_buffer = 0.0f;
    current_volt -= leak_rate;
    if (current_volt < 0.0f)
        current_volt = 0.0f;

    if (current_volt >= threshold)
    {
        is_fired = true;
        current_volt = 0.0f;
        refractory_time = 2;
    }
    else
        is_fired = false;
}

void Neuron::add_to_buffer(float v)
{
    volt_buffer += v;
}