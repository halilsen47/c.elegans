#ifndef BRAIN_H
#define BRAIN_H
#include <cstdint>
#include <iostream>
#include "Neuron.h"
#include <unordered_map>
#include <string>
#include <fstream>
#include <sstream>

struct Synapse
{
    uint16_t source;
    uint16_t target;
    float weight;
    uint8_t type;
};

class Brain
{
private:
    Neuron neurons[1000];
    Synapse synapses[7380];
    uint16_t sensor_ids[4];
    uint16_t command_ids[4];
    std::string neuron_names[1000];

public:
    void tick(float *sensor_input, uint8_t input_count, bool *command_output, uint8_t output_count);
    void set_weights(float *new_weights);
    void print_network_activity(int current_tick);
    uint16_t total_nodes = 0;
    Brain(/* args */);
};

#endif