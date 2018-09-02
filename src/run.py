import random
from src.conf import Conf, ConfSample
import src.dataset as Dataset
from src.model import Model
import pandas as pd
import tensorflow as tf

'''
Used to either train a new model or test an exiting one (if you simply want to PREDICT methylation values, i.e. you're
not interested in training a model - use predict.py).
You have two options: 
(1) Train the model from scratch using load_model = 0 or 
(2) Train with an existing model (transfer learning) using load_model = 1/2/3 according to your needs (if your CpG 
is within a 2K of one of the genes in the run_example file, choose 1, if within 10K choose 2 etc. according to paper. If
you're not sure - either contact us (alonal at cs.technion.ac.il) or simply use the most general model - 3). 
As the weights are large files (~1G) please contact us and we will send them directly to you. In the near future they 
will be available directly for download.
Note - the model's naming convention for checkpoint purposes is long (deliberately so that you know which parameters it includes). However,
TensorFlow doesn't recognize these long names when loading them, so before loading - rename the relevant checkpoint files to a short name, with no
special characters. 
'''

####  YOUR SETTINGS - START ####

load_model_ID = 2  #see explanation above
test_time = True   # when you want to test on the test set, which was automatically generated for each of the files you supplied in your conf settings.
save_models = False # choose true if you want to save the model while training (will be saved automatically if performance is good or if 90 minutes have passed - see model.py)

####  YOUR SETTINGS - END ####


sample = True
if sample:
    Conf = ConfSample

train, validation, test, validation_ch3_blind, test_ch3_blind, validation_e_blind, test_e_blind = Dataset.read_data_sets(
    filename_sequence=Conf.filename_sequence,
    filename_expression=Conf.filename_expression,
    filename_labels=Conf.filename_labels,
    filename_dist=Conf.filename_dist,
    train_portion_subjects=Conf.train_portion_probes,
    train_portion_probes=Conf.train_portion_probes, validation_portion_subjects=Conf.validation_portion_subjects,
    validation_portion_probes=Conf.validation_portion_probes, directory='../res/', load_model_ID=load_model_ID)

# train, validation, test, validation_ch3_blind, test_ch3_blind, validation_e_blind, test_e_blind = None, None, None, None, None, None, None

d = pd.read_csv('../res/' + Conf.filename_expression, nrows=1)
n_genes = len(d.columns)-1

learning_rates = [0.001, 0.0001, 0.00001, 0.000001, 0.0000001, 0.00000001]
n_runs = range(len(learning_rates))
ff_hidden_units = [[50,0] for i in n_runs]
ff_n_hidden = 3
conv_filters = [64 for i in n_runs]
conv_pools = [10 for i in n_runs]
conv_strides = [10 for i in n_runs]
connected_hidden_units = [[50,0] for i in n_runs]
connected_n_hidden = 3
reg_scales = [0.0 for i in n_runs]
optimizers = [tf.train.AdamOptimizer for i in n_runs]
losses = [tf.losses.absolute_difference for i in n_runs]
model_name_suffix = 'test'

if sample:
    learning_rates = [0.001, 0.0001, 0.00001, 0.000001, 0.0000001, 0.00000001]


for counter in range(len(learning_rates)):
    print("starting new model with counter %d" %counter)
    regularization_scale = reg_scales[counter]
    multiplyNumUnitsBy = 1
    numLayers = 0
    neighborAlpha = 0
    c = "all"
    lr = learning_rates[counter]
    n_quant = 10
    ff_h = ff_hidden_units[counter]
    conv_f = conv_filters[counter]
    conv_p = conv_pools[counter]
    conv_s = conv_strides[counter]
    connected_h = connected_hidden_units[counter]

    modelID = str(lr) + "_" + str(ff_h[0]) +"_"+str(conv_f)+"_"+str(conv_p)+"_"+str(connected_h)+"_"+str(random.randint(0,1000))\
              +"_"+str(optimizers[counter]).split(".")[-2]+"_"+str(losses[counter]).split(" ")[1]+model_name_suffix
    model = Model(sample, modelID,lr, multiplyNumUnitsBy, n_quant, neighborAlpha, c,
          ff_h[0], ff_h[1], conv_f, conv_p, conv_s, connected_h[0], connected_h[1], regularization_scale,
                 train, validation, test, validation_ch3_blind, test_ch3_blind, validation_e_blind, test_e_blind, n_genes,
                  ff_n_hidden, connected_n_hidden, optimizers[counter], losses[counter], load_model=load_model_ID, test_time=test_time, save_models=save_models, save_weights=test_time, is_prediction=False)
    model.build(with_autoencoder=False)
    tf.reset_default_graph()

