#include "ai_app.h"

ai_handle network;
float aiOutData[AI_NETWORK_OUT_1_SIZE];
uint8_t activations[AI_NETWORK_DATA_ACTIVATIONS_SIZE];
static ai_network_report network_info;

static void ai_log_err(const ai_error err, const char *fct);
static int ai_boostrap(ai_handle w_addr, ai_handle act_addr);


static void ai_log_err(const ai_error err, const char *fct)
{
    if (fct)
        printf("TEMPLATE - Error (%s) - type=0x%02x code=0x%02x\r\n", fct, err.type, err.code);
    else
        printf("TEMPLATE - Error - type=0x%02x code=0x%02x\r\n", err.type, err.code);
}

static int ai_boostrap(ai_handle w_addr, ai_handle act_addr)
{
    ai_error err;

    /* 1 - Create an instance of the model */
    err = ai_network_create(&network, AI_NETWORK_DATA_CONFIG);
    if (err.type != AI_ERROR_NONE)
    {
        ai_log_err(err, "ai_network_create");
        return -1;
    }

    /* 2 - Initialize the instance */
    const ai_network_params params = AI_NETWORK_PARAMS_INIT(
        AI_NETWORK_DATA_WEIGHTS(w_addr),
        AI_NETWORK_DATA_ACTIVATIONS(act_addr));

    if (!ai_network_init(network, &params))
    {
        err = ai_network_get_error(network);
        ai_log_err(err, "ai_network_init");
        return -1;
    }

    /* 3 - Retrieve the network info of the created instance */
    if (!ai_network_get_info(network, &network_info))
    {
        err = ai_network_get_error(network);
        ai_log_err(err, "ai_network_get_error");
        ai_network_destroy(network);
        network = AI_HANDLE_NULL;
        return -3;
    }
    return 0;
}

int ai_Init(void)
{
	int res = ai_boostrap(ai_network_data_weights_get(),activations);
	return res;
}

int ai_Run(void *data_in, void *data_out)
{
    ai_i32 batch;

    ai_buffer *ai_input = network_info.inputs;
    ai_buffer *ai_output = network_info.outputs;

    ai_input[0].data = AI_HANDLE_PTR(data_in);
    ai_output[0].data = AI_HANDLE_PTR(data_out);

    batch = ai_network_run(network, ai_input, ai_output);
    if (batch != 1)
    {
        ai_log_err(ai_network_get_error(network), "ai_network_run");
        return -1;
    }

    return 0;
}