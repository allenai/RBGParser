from collections import namedtuple

new_system = 'gold'

Instance = namedtuple('Instance', 'children_words heads_words gold_head_word new_system_head_word preps_words'.split(' '), verbose=True)

# load the data scattered in different files, one preposition per line.
def read_one_preposition_per_line(children_words_filename,
                                  heads_words_filename,
                                  labels_filename,
                                  new_system_predictions_filename,
                                  preps_words_filename):
  instances=[]
  with open(children_words_filename) as children_words_file, \
          open(heads_words_filename) as heads_words_file, \
          open(labels_filename) as labels_file, \
          open(new_system_predictions_filename) as new_system_predictions_file, \
          open(preps_words_filename) as preps_words_file:
    while True:
      heads_words_line = heads_words_file.readline().strip()
      if heads_words_line == '': break
      heads_words = heads_words_line.split(' ')
      instance = Instance(children_words=children_words_file.readline().strip(), \
                            heads_words=heads_words, \
                            gold_head_word=heads_words[int(labels_file.readline().strip())-1], \
                            new_system_head_word=heads_words[int(new_system_predictions_file.readline().strip())-1], \
                            preps_words=preps_words_file.readline().strip())
      instances.append(instance)
  return instances

print('before defining train_instances')
train_instances = read_one_preposition_per_line("wsj.2-21.txt.dep.pp.children.words",
                                                "wsj.2-21.txt.dep.pp.heads.words",
                                                "wsj.2-21.txt.dep.pp.labels",
                                                "wsj.2-21.txt.dep.pp." + new_system + ".predictions",
                                                "wsj.2-21.txt.dep.pp.preps.words")

print('before defining test_instances')
test_instances = read_one_preposition_per_line("wsj.23.txt.dep.pp.children.words",
                                                "wsj.23.txt.dep.pp.heads.words",
                                                "wsj.23.txt.dep.pp.labels",
                                                "wsj.23.txt.dep.pp." + new_system + ".predictions",
                                                "wsj.23.txt.dep.pp.preps.words")

print('before defining get_instance_indeices')
def get_instance_index(instances, likely_index, preps_words, gold_head_word,
                         heads_words_candidates):
  preps_words = preps_words.lower()
  gold_head_word = gold_head_word.lower()
  heads_words_candidates = [word.lower() for word in heads_words_candidates]
  attempts = 0
  for i in range(likely_index, len(instances)):
    if i != likely_index:
      pass
    attempts += 1
    if attempts > 10:
      import pdb; pdb.set_trace()
    instance = instances[i]
    if preps_words.lower() != instance.preps_words: continue
    if gold_head_word.lower() != instance.gold_head_word: continue
    compatible = True
    for head_candidate in instance.heads_words:
      if head_candidate not in heads_words_candidates:
        compatible = False
        break
    if not compatible: continue
    # any instance which hasn't been excluded at this point is compatible.
    return i
  assert(False)

print('before defining yonatan_conll_filenames')
yonatan_conll_filenames = ['wsj.2-21.txt.dep.pp.yonatan.predictions.conll',
                       'wsj.23.txt.dep.pp.yonatan.predictions.conll']

print('before processing conll files')
for conll_filename in yonatan_conll_filenames:
  instances = train_instances if conll_filename.startswith('wsj.2-21') else test_instances 
  new_system_conll_filename = conll_filename.replace('yonatan', new_system)
  with open(conll_filename) as conll_file, open(new_system_conll_filename, mode='w') as new_system_conll_file:
    sent_buffer = []
    preps_counter = -1
    for line in conll_file:
      if len(line.strip()) > 1:
        # add token to sentence buffer.
        sent_buffer.append(line.strip())
      else:
        # process sentence.
        for token_index, token_line in enumerate(sent_buffer):
          if token_line.endswith('_'): 
            new_system_conll_file.write(token_line + '\n')
            continue
          preps_counter += 1
          fields = token_line.split('\t')
          assert(token_index == int(fields[0])-1)
          preps_words = fields[1].lower()
          gold_head_word = sent_buffer[int(fields[6])-1].split('\t')[1].lower()
          #if preps_counter == 22:
          #  import pdb; pdb.set_trace()
          children_words_candidates = [sent_buffer[i].split('\t')[1].lower() \
                                           for i \
                                           in range(token_index+1, len(sent_buffer))]
          heads_words_candidates = [sent_buffer[i].split('\t')[1].lower() \
                                        for i \
                                        in range(0, token_index)]
          # instead of searching for a comatible index, check instances[preps_counter].
          # if it doesn't fit the bill, check instances[preps_counter+1] ...etc.
          # until you find one that matches.
          preps_counter = get_instance_index(instances,
                                             preps_counter,
                                             preps_words, 
                                             gold_head_word, 
                                             heads_words_candidates)
          # write next prediction.
          new_system_head_word = instances[preps_counter].new_system_head_word.lower()
          new_system_head_id = None
          for head_index in reversed(range(0, token_index)):
            if sent_buffer[head_index].split('\t')[1].lower() == new_system_head_word:
              new_system_head_id = head_index + 1
          if new_system_head_id == None:
            print('ERROR: couldn\'t find the head word predicted by new_system in the same sentence')
            import pdb; pdb.set_trace()
            assert(False)
          # replace yonatan's prediction with new_system prediction.
          fields[-1] = str(new_system_head_id)
          new_system_conll_file.write('\t'.join(fields) + '\n')
        sent_buffer.clear()
        new_system_conll_file.write('\n')
