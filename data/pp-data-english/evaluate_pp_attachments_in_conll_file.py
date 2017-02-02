yonatan_conll = 'wsj.23.txt.dep.pp.yonatan.predictions.conll'
other_conll = 'wsj.23.txt.dep.pp.lstm.predictions.conll'
predicted_head_index = 6 if other_conll.endswith('.rgbout') else -1

correct, incorrect = 0., 0.
line_number=0
for yonatan_line, other_line in zip(open(yonatan_conll), open(other_conll)):
  line_number += 1
  # skip empty lines.
  if len(yonatan_line.strip()) == 0: continue
  # skip lines where yonatan didn't make a pp attachment prediction.
  if yonatan_line.strip().endswith('_'): continue
  # find the correct head index
  gold_head = yonatan_line.strip().split('\t')[6]
  # find the predicted head index
  predicted_head = other_line.strip().split('\t')[predicted_head_index]
  if gold_head == predicted_head:
    correct += 1.
  else:
    print('incorrect head at line #{}'.format(line_number))
    incorrect += 1.

accuracy = correct / (correct + incorrect)
print('accuracy={}% ({} correct, {} incorrect, {} total)'.format(100 * accuracy, correct, incorrect, correct+incorrect))
