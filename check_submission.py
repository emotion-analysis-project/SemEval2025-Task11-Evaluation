import os
import sys
import argparse
from statistics import mean
from tabulate import tabulate

from utils import check_file_name, check_files, check_if_language_is_supported, evaluate, evaluate_b, get_task_details, zip_file

parser = argparse.ArgumentParser(description='Checking file submission format.')
parser.add_argument('-s', '--submission_file', type=str, required=True, help='Submission file path.')
parser.add_argument('-p', '--phase', type=str, required=True, help='Phase of the competition (dev or test).')
parser.add_argument('--evaluate', action='store_true', help='Evaluate the submission file.')
parser.add_argument('-g', '--gold_data', type=str, help='Path to the gold data file.', default='')
parser.add_argument('--zip_for_submission', action='store_true', help='Zip the submission file.')
args = parser.parse_args()

submission_file = args.submission_file
gold_data_path = args.gold_data
phase = args.phase

language, task = get_task_details(submission_file)
if not check_if_language_is_supported(language):
  sys.exit(f'\nData for {language} track {task} is not included in the shared task: SemEval-2025 Task 11.\nVisit the competition page (https://github.com/emotion-analysis-project/SemEval2025-Task11) for more details.')
else:
  print('\n==============')
  print('Checklist:')
  print('==============')

  checklist = check_file_name(submission_file)
  print(tabulate(checklist, headers=['Item', 'Status', 'Comment'], tablefmt='grid'))

  if args.zip_for_submission:
    print('\nZipping the submission file...')
    zip_file(submission_file)

  if args.evaluate:
    if not gold_data_path:
      sys.exit('\nGold data file path is required for evaluation.')
    if not os.path.exists(gold_data_path):
      sys.exit('\nGold data file not found.')

    print('\nEvaluating submission file...')
    gold_lines, pred_lines = check_files(gold_data_path, submission_file)

    if task == 'b':
      emotion_r = evaluate_b(gold_lines, pred_lines)
      print(f'Evaluation scores for {language} track B:\n')
      for emotion, score in emotion_r.items():
        print(f'{emotion} Pearson r: {score}')
      print(f'\nAverage Pearson r: {round(mean(emotion_r.values()), 4)}')
    else:
      eval_scores = evaluate(gold_lines, pred_lines)
      for average in eval_scores:
        print(f'Evaluation scores ({average}) for {language} track {task}:')
        print('Precision:', eval_scores[average]['precision'])
        print('Recall:', eval_scores[average]['recall'])
        print('F1 score:', eval_scores[average]['f1'])
        print()