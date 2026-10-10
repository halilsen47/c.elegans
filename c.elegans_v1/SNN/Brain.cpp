#include "Brain.h"
#include <algorithm>
#include <cctype>
#include <cstdlib>
#include <ctime>
std::string clean_node_name(const std::string &s)
{
    std::string result = "";
    for (char c : s)
    {
        if (std::isalnum(c))
            result += c;
    }
    return result;
}

Brain::Brain()
{
    std::unordered_map<std::string, uint16_t> hand_book;
    uint16_t next_id = 0;

    std::ifstream file("herm_full_edgelist.csv");
    if (!file.is_open())
    {
        std::cerr << "HATA: CSV bulunamadi!" << std::endl;
        return;
    }

    std::string line;
    std::getline(file, line);

    for (size_t i = 0; i < 7379; i++)
    {
        if (!std::getline(file, line) || line.empty())
            break;

        std::stringstream ss(line);
        std::string src_str, tgt_str, weight_str, type_str;

        std::getline(ss, src_str, ',');
        std::getline(ss, tgt_str, ',');
        std::getline(ss, weight_str, ',');
        std::getline(ss, type_str, ',');

        src_str = clean_node_name(src_str);
        tgt_str = clean_node_name(tgt_str);

        if (src_str.empty() || tgt_str.empty())
            continue;

        float w = 0.0f;
        try
        {
            w = std::stof(weight_str);
        }
        catch (...)
        {
            continue;
        }

        uint8_t t = 0;
        if (type_str.find("electrical") != std::string::npos || type_str.find("Electrical") != std::string::npos)
            t = 1;

        if (hand_book.find(src_str) == hand_book.end())
        {
            hand_book[src_str] = next_id;
            neuron_names[next_id] = src_str;
            next_id++;
        }
        if (hand_book.find(tgt_str) == hand_book.end())
        {
            hand_book[tgt_str] = next_id;
            neuron_names[next_id] = tgt_str;
            next_id++;
        }

        synapses[i].source = hand_book[src_str];
        synapses[i].target = hand_book[tgt_str];
        synapses[i].weight = w;
        synapses[i].type = t;
    }
    file.close();

    total_nodes = next_id;
    // std::cout << "Baglanti kurulumu bitti. Toplam benzersiz noron: " << total_nodes << std::endl;

    sensor_ids[0] = hand_book["ASIL"];
    sensor_ids[1] = hand_book["ASIR"];
    sensor_ids[2] = hand_book["ASHL"];
    sensor_ids[3] = hand_book["ASHR"];

    command_ids[0] = hand_book["AVB"];
    command_ids[1] = hand_book["AVA"];
    command_ids[2] = hand_book["RIML"];
    command_ids[3] = hand_book["RIMR"];
}

void Brain::tick(float *sensor_input, uint8_t input_count, bool *command_output, uint8_t output_count)
{

    // iligli nöron ile input eşleştirme
    for (size_t i = 0; i < input_count; i++)
    {
        neurons[sensor_ids[i]].add_to_buffer(sensor_input[i]);
    }

    // buffer sistemini çalıştırma
    for (size_t i = 0; i < 7380; i++)
    {
        uint16_t source = synapses[i].source;
        uint8_t type = synapses[i].type;
        if (type == 0)
        {
            if (neurons[source].fired())
            {
                neurons[synapses[i].target].add_to_buffer(synapses[i].weight);
            }
        }
        else if (type == 1)
        {
            if (neurons[source].get_voltage() > 0.0f)
            {
                neurons[synapses[i].target].add_to_buffer(synapses[i].weight);
            }
        }
    }

    // nöronları senkron bir şekilde güncelleme
    for (size_t i = 0; i < total_nodes; i++)
        neurons[i].step();

    // çıkış komutlarının kontrol edilmesi
    for (size_t i = 0; i < output_count; i++)
        command_output[i] = neurons[command_ids[i]].fired();
}

void Brain::set_weights(float *new_weights)
{
    for (size_t i = 0; i < 7380; i++)
    {
        synapses[i].weight = new_weights[i];
    }
}

void Brain::print_network_activity(int current_tick)
{
    std::cout << "--- TICK " << current_tick << " ---" << std::endl;
    bool any_fired = false;

    for (int i = 0; i < total_nodes; i++)
    {
        if (neurons[i].fired())
        {
            std::cout << " [*] ATESLENDI: " << neuron_names[i] << std::endl;
            any_fired = true;
        }
    }

    if (!any_fired)
    {
        std::cout << " [ ] Agda sessizlik..." << std::endl;
    }
    std::cout << std::endl;
}

extern "C"
{
    __declspec(dllexport) Brain *Brain_new()
    {
        return new Brain();
    }

    __declspec(dllexport) void Brain_set_weights(Brain *brain, float *new_weights)
    {
        brain->set_weights(new_weights);
    }

    __declspec(dllexport) void Brain_tick(Brain *brain, float *sensor_input, uint8_t input_count, bool *command_output, uint8_t output_count)
    {
        brain->tick(sensor_input, input_count, command_output, output_count);
    }

    __declspec(dllexport) void Brain_delete(Brain *brain)
    {
        delete brain;
    }
}