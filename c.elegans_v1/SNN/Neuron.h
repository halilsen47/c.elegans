#ifndef NEURON_H
#define NEURON_H

class Neuron
{
private:
    float current_volt = 0.0f;
    float volt_buffer = 0.0f;
    float leak_rate = 0.1f;
    float threshold = 1.0f;
    bool is_fired = false;
    int refractory_time = 0;

public:
    Neuron(/* args */);

    void step();
    bool fired() { return this->is_fired; }
    float get_voltage() const { return current_volt; }
    void add_to_buffer(float w);
};

#endif