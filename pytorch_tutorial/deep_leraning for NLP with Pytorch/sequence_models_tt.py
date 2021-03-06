
import torch
import torch.autograd as autograd
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim


torch.manual_seed(1)

lstm = nn.LSTM(3,3) # imput dim is 3, output dim is 3
inputs = [autograd.Variable(torch.randn((1,3))) for _ in range(5)]
            # make a sequence of length 5

#print(inputs)
            
# initialized the hidden state.
hidden = (autograd.Variable(torch.randn(1, 1, 3)),  # size dim? 
          autograd.Variable(torch.randn((1, 1, 3)))) # size dim?


#print(hidden)

for i in inputs:
    # Step through the sequence on element at a time.
    # after each step, hidden contains the hidden state.
    out, hidden = lstm(i.view(1, 1, -1), hidden)
    
# alternatively, we can do the entire sequence all at once.
# the fist value returned by LSTM is all of the hidden states throuhout
# the sequence. the second is just the most recent hidden state
# (compare the last slice of "out" with below, they are the same)
# "out" will give out access to all hidden states in the sequence
# "hidden" will allow you to continue the sequence and backpropagate.
# by passing it as an argument to the lstm at a later time
# Add the extra 2nd dimension  -> ??

inputs = torch.cat(inputs).view((len(inputs), 1, -1))  # data dimension convert is so confused...

#print(inputs)

hidden = (autograd.Variable(torch.randn(1, 1, 3)), autograd.Variable( torch.randn((1, 1, 3)))) # clean out hidden state
out, hidden = lstm(inputs, hidden)
print(out)
print()
print(hidden)  # hidden is why 2x3?


# Example: An LSTM for part-of-speech Tagging

def prepare_sequence(seq, to_ix):
    idxs  = [to_ix[w] for w in seq]
    tensor = torch.LongTensor(idxs)
    return autograd.Variable(tensor)


training_data = [
    ("The dog ate the apple".split(), ["DET", "NN", "V", "DET", "NN"]),
    ("Everybody read that book".split(),["NN", "V", "DET", "NN"])
    ]

word_to_ix={}
for sent, tags in training_data:
    for word in sent:
        if word not in word_to_ix:
            word_to_ix[word] = len(word_to_ix)

print(word_to_ix)
tag_to_ix = {"DET": 0, "NN":1, "V": 2}  # class : dictionary
 
# These will usally be more like 32 or 64 dimension
# We will keep them small, so we see how the weights changes as we train.
EMBEDDING_DIM = 6
HIDDEN_DIM = 6


# Create the model:

class LSTMTagger(nn.Module):
    def __init__(self, embedding_dim, hidden_dim, vocab_size, tagset_size):
        super(LSTMTagger, self).__init__()
        self.hidden_dim = hidden_dim
        
        self.word_embeddings = nn.Embedding(vocab_size, embedding_dim)
        
        # The LSTM takes word embeddings as inputs, and outputs hdden states
        # with dimensionality hidden_dim.
        self.lstm = nn.LSTM(embedding_dim, hidden_dim)
        
        # The linear layer that maps from hidden state space to tag space
        self.hidden2tag = nn.Linear(hidden_dim, tagset_size)
        self.hidden = self.init_hidden()
        
    def init_hidden(self):
        # Before we've done anythung, we dont have any hidden state.
        # Refer to the Pytorch documentation to see exactly
        # why they have this dimensionality.
        # the axes semantics are (num_layers, minibatch_size, hidden_dim)
        return (autograd.Variable(torch.zeros(1, 1, self.hidden_dim)),
                autograd.Variable(torch.zeros(1, 1, self.hidden_dim)))
    
    def forward(self, sentence):
        embeds = self.word_embeddings(sentence)
        lstm_out, self.hidden = self.lstm( embeds.view(len(sentence), 1, -1), self.hidden)
        tag_space = self.hidden2tag(lstm_out.view(len(sentence), -1))
        tag_scores = F.log_softmax(tag_space)
        return tag_scores
    
    
# Trin the model:

model = LSTMTagger(EMBEDDING_DIM, HIDDEN_DIM, len(word_to_ix), len(tag_to_ix))
loss_function = nn.NLLLoss()
optimizer = optim.SGD(model.parameters(), lr = 0.1)

# See what the scores are before training
# Note that element i, j of output is the score for tag j for word i
inputs = prepare_sequence(training_data[0][0], word_to_ix)
tag_scores = model(inputs)
print(tag_scores)

for epoch in range(300): # again, normally you would not do 300 epochs, it is toy data
    for sentence, tags in training_data:
        # Step 1. Remembet that pytorch accumulates gradients
        # we need to clear them out before each instance
        model.zero_grad()
        
        # Also, we nee to clear out the hidden state of the LSTM,
        # detaching it from its history on the last instamce.
        model.hidden = model.init_hidden()
        
        # Step 2. get our inputs ready for the network, that is turn them into
        # variables of word indices.
        
        sentence_in = prepare_sequence(sentence, word_to_ix)
        targets = prepare_sequence(tags, tag_to_ix)
        
        # step 3. Run our forward pass.
        tag_scores = model(sentence_in)       

        
        # step 4. Compute the loss, gradients. and updates the parameters by
        # calling optimizer.step()
        loss = loss_function(tag_scores, targets)
        loss.backward()        
        optimizer.step()
        
# see whar the scores are after trining
inputs = prepare_sequence(training_data[0][0], word_to_ix)
tag_scores = model(inputs)
# the sentence is "the dog ate the apple". i, j, corresponds to score for tag j
# Here, we can see the predicted sequence below is 0 1 2 0 1
# since 0 is index of the maximum value of row 1,
# 1 is the index of maximum value of row 1,
# which is DE NOUN VERB DET NOUN, the correnct sequence1

print(tag_scores)



        
        
        
        
        
    
    

                
        
    



    
                     


            