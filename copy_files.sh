# הגדרות נתיבים
OLD_PATH="/home/nlp/davidoy5/XQASem"
NEW_PATH="/home/nlp/davidoy5/crosslingual-qasem"

# העתקת קבצים למיקומים החדשים
cp "$OLD_PATH/conll_to_df.py"              "$NEW_PATH/scripts/preprocess/"
cp "$OLD_PATH/base_target_alignment.py"    "$NEW_PATH/scripts/alignment/"
cp "$OLD_PATH/create_en_qasem.py"          "$NEW_PATH/scripts/projection/"
cp "$OLD_PATH/base_to_target_qasem.py"     "$NEW_PATH/scripts/projection/"
cp "$OLD_PATH/questions.py"                "$NEW_PATH/scripts/qa/"
cp "$OLD_PATH/answers.py"                  "$NEW_PATH/scripts/qa/"
cp "$OLD_PATH/qa_nom.py"                   "$NEW_PATH/scripts/qa/"
cp "$OLD_PATH/qasrl_he_predicate.py"       "$NEW_PATH/scripts/predicates/qasem_predicate.py"  # עם שינוי שם
cp "$OLD_PATH/utils_func.py"               "$NEW_PATH/utils/"
cp "$OLD_PATH/few_shots.py"                "$NEW_PATH/utils/"
