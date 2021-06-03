import os
import torch
from typing import List
from multilingual_ft.config.language import Language
from collections import defaultdict
class MultilingualTrainingState():
    def __init__(self,src:str,languages: List[str],model_dir:str,early_stopping_step:int=3,eval_with_source: bool=False,eval_with_average=True,exp_name=""):
        self.early_stopping_step = early_stopping_step
        self.src=src
        self.src_loss=[]
        self.src_eval=[]
        self.src_best = -1
        self.eval_with_source = eval_with_source
        self.model_dir = model_dir
        self.exp_name=exp_name

        for lang in languages:
            if not os.path.exists(os.path.sep.join([self.model_dir,lang])):
                os.mkdir(os.path.sep.join([self.model_dir,lang]))

        self.languages=languages[:]
        self.stop_early=defaultdict(lambda:False)
        self.early_stopping_steps= defaultdict(lambda: 0)
        self.target_eval= defaultdict(list)
        self.target_loss = defaultdict(list)
        self.target_best = defaultdict(lambda:-1)
        self.eval_with_average=eval_with_average
        self.epoch_idx=-1
        self.average_loss=[]
        self.average_score=[]
        self.average_best=-1

    def update_and_save(self,model,results):
        self.epoch_idx+=1
        self.src_loss.append(results[self.src]["loss"])
        self.src_eval.append(results[self.src]["score"])
        ##only got src evals
        if self.eval_with_source:
            if self.epoch_idx == 0:
                torch.save(model.state_dict(), os.path.sep.join([self.model_dir, ",model.bin"]))
                self.stop_early["src"] = False
                self.src_best=results[self.src]["score"]
                return True
            else:
                score_tm1, score_t = self.src_eval[-2:]
                if score_t <= score_tm1:
                    # Update step
                    self.early_stopping_steps["src"] += 1
                else:
                    if score_t > self.src_best:
                        self.src_best =results[self.src]["score"]
                        torch.save(model.state_dict(), os.path.sep.join([self.model_dir, ",model.bin"]))
                    self.early_stopping_steps["src"] = 0
                if self.early_stopping_steps["src"] >=self.early_stopping_step:
                    self.stop_early["src"]=True
                    return False
                return True

        elif self.eval_with_average:
            avg_score=0.
            avg_loss=0.
            for lang in self.languages:
                avg_score+=results[lang]["score"]
                avg_loss+=results[lang]["loss"]
            avg_score=avg_score/len(self.languages)
            avg_loss=avg_loss/len(self.languages)
            self.average_loss.append(avg_loss)
            self.average_score.append(avg_score)
            if self.exp_name!="":
                with open(os.path.sep.join([self.model_dir, self.exp_name]),"w") as f:
                    out=",".join(str(x) for x in self.average_score)
                    f.write(out)
            if self.epoch_idx == 0:
                torch.save(model.state_dict(), os.path.sep.join([self.model_dir, ",model.bin"]))
                self.stop_early["avg"] = False
                self.average_best=avg_score
                return True
            else:
                score_tm1, score_t = self.average_score[-2:]
                if score_t <= score_tm1:
                    # Update step
                    self.early_stopping_steps["avg"] += 1
                else:
                    if score_t > self.average_best:
                        self.average_best =avg_score
                        torch.save(model.state_dict(), os.path.sep.join([self.model_dir, ",model.bin"]))
                    self.early_stopping_steps["avg"] = 0
                if self.early_stopping_steps["avg"] >=self.early_stopping_step:
                    self.stop_early["avg"]=True
                    return False
                return True
        else: ## separage_training
            for lang in self.languages:
                if not self.stop_early[lang]:##is still training
                    print(lang)
                    self.target_loss[lang].append(results[lang]["loss"])
                    self.target_eval[lang].append(results[lang]["score"])
                    if self.epoch_idx== 0:
                        torch.save(model.state_dict(), os.path.sep.join([self.model_dir,lang,",model.bin"]))
                        self.target_best[lang] = self.target_eval[lang][-1]
                        self.stop_early[lang] = False
                    else:
                        score_tm1, score_t = self.target_eval[lang][-2:]
                        if score_t <= score_tm1:
                            # Update step
                            self.early_stopping_steps[lang] += 1
                        else:
                            if score_t > self.target_best[lang]:
                                torch.save(model.state_dict(), os.path.sep.join([self.model_dir, lang, ",model.bin"]))
                                self.target_best[lang]=score_t
                            self.early_stopping_steps[lang]=0
                        if self.early_stopping_steps[lang]>=self.early_stopping_step:
                            ##wont test it any more
                            self.stop_early[lang] = True
            if all ([self.stop_early[lang] for lang in self.languages]):
                return False
            return True


