
import openai
from time import sleep
from openai.error import RateLimitError, APIConnectionError
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import TerminalFormatter
from utils import load_prompt, DynamicObservation, IterableDynamicObservation
import time
from LLM_cache import DiskCache


class LanguageModelProgram:
    """Language Model Program (LMP), adopted from Code as Policies."""
    
    def __init__(self, name: str, config: dict, fixed_variables: dict, variable_vars: dict, debug: bool = False, env="rlbench"):
        self._name = name
        self._config = config
        self._debug = debug
        self._base_prompt = load_prompt(f"{env}/{config['prompt_fname']}.txt")
        self._stop_tokens = list(config['stop'])
        self._fixed_variables = fixed_variables
        self._variable_vars = variable_vars
        self.execution_history = ""
        self._context = None
        self._cache = DiskCache(load_cache=config['load_cache'])

    def clear_execution_history(self):
        self.execution_history = ''

    def build_prompt(self, query):
        if len(self._variable_vars) > 0:
            variable_vars_imports_str = f"from utils import {', '.join(self._variable_vars.keys())}"
        else:
            variable_vars_imports_str = ''
        prompt = self._base_prompt.replace('{variable_vars_imports}', variable_vars_imports_str)

        if self._config['maintain_session'] and self.execution_history != '':
            prompt += f'\n{self.execution_history}'
        
        prompt += '\n'  # separate prompted examples with the query part

        if self._config['include_context']:
            assert self._context is not None, 'context is None'
            prompt += f'\n{self._context}'

        user_query = f'{self._config["query_prefix"]}{query}{self._config["query_suffix"]}'
        prompt += f'\n{user_query}'

        return prompt, user_query
    
    def update_prompt_message(self, **kwargs):
        # add special prompt for chat endpoint
        print('construct prompt')
        user1 = kwargs.pop('prompt')
        new_query = '# Query:' + user1.split('# Query:')[-1]
        user1 = ''.join(user1.split('# Query:')[:-1]).strip()
        user1 = f"I would like you to help me write Python code to control a robot arm operating in a tabletop environment. Please complete the code every time when I give you new query. Pay attention to appeared patterns in the given context code. Be thorough and thoughtful in your code. Do not include any import statement. Do not repeat my question. Do not provide any text explanation (comment in code is okay). I will first give you the context of the code below:\n\n```\n{user1}\n```\n\nNote that x is back to front, y is left to right, and z is bottom to up. Please note \n is the line break. Do not add \ in the result"
        assistant1 = f'Got it. I will complete what you give me next.'
        user2 = new_query
        # handle given context (this was written originally for completion endpoint)
        if user1.split('\n')[-4].startswith('objects = ['):
            obj_context = user1.split('\n')[-4]
            # remove obj_context from user1
            user1 = '\n'.join(user1.split('\n')[:-4]) + '\n' + '\n'.join(user1.split('\n')[-3:])
            # add obj_context to user2
            user2 = obj_context.strip() + '\n' + user2
        messages= [
            {"role": "system", "content": "You are a helpful assistant that pays attention to the user's instructions and writes good python code for operating a robot arm in a tabletop environment."},
            {"role": "user", "content": user1},
            {"role": "assistant", "content": assistant1},
            {"role": "user", "content": user2},
        ]
        kwargs['messages'] = messages
        return kwargs


    def _cached_api_call(self, **kwargs):
        # check whether completion endpoint or chat endpoint is used
        if kwargs in self._cache:
            print('(using cache)', end=' ')
            return self._cache[kwargs]
        else:
            if kwargs['model'] != 'gpt-3.5-turbo-instruct' and any([chat_model in kwargs['model'] for chat_model in ['gpt-3.5', 'gpt-4', 'mixtral-8x7b']]):
                kwargs = self.update_prompt_message(**kwargs)
                ret = openai.ChatCompletion.create(**kwargs)['choices'][0]['message']['content']
                # post processing
                ret = ret.replace('```', '').replace('python', '').strip()
                self._cache[kwargs] = ret
                return ret
            else:
                ret = openai.Completion.create(**kwargs)['choices'][0]['text'].strip()
                self._cache[kwargs] = ret
                return ret

    def __call__(self, query, **kwargs):
        """
        This function executes the language model program with a given query.
        
        Args:
            query (str): The query to be executed.
            kwargs: Additional keyword arguments for the execution.
            
        Returns:
            The result of the execution based on the configuration.
        """
        prompt, user_query = self.build_prompt(query)

        start_time = time.time()
        while True:
            try:
                code_str = self._cached_api_call(
                    prompt=prompt,
                    stop=self._stop_tokens,
                    temperature=self._config['temperature'],
                    model=self._config['model'],
                    max_tokens=self._config['max_tokens']
                )
                break
            except (RateLimitError, APIConnectionError) as e:
                print(f'OpenAI API got err {e}')
                print('Retrying after 3s.')
                sleep(3)
        print(f'*** OpenAI API call took {time.time() - start_time:.2f}s ***')

        if self._config['include_context']:
            assert self._context is not None, 'context is None'
            to_exec = f'{self._context}\n{code_str}'
            to_log = f'{self._context}\n{user_query}\n{code_str}'
        else:
            to_exec = code_str
            to_log = f'{user_query}\n{to_exec}'

        to_log_pretty = highlight(to_log, PythonLexer(), TerminalFormatter())

        if self._config['include_context']:
            print('#'*40 + f'\n## "{self._name}" generated code\n' + f'## context: "{self._context}"\n' + '#'*40 + f'\n{to_log_pretty}\n')
        else:
            print('#'*40 + f'\n## "{self._name}" generated code\n' + '#'*40 + f'\n{to_log_pretty}\n')

        global_vars = merge_dicts([self._fixed_variables, self._variable_vars])
        local_vars = kwargs

        # return function instead of executing it so we can replan using latest observations
        if not self._name in ['composer', 'planner']:
            to_exec = 'def ret_val():\n' + to_exec.replace('ret_val = ', 'return ')
            to_exec = to_exec.replace('\n', '\n    ')

        if self._debug:
            # only "execute" function performs actions in environment, so we comment it out
            action_str = ['execute(']
            try:
                for s in action_str:
                    exec_safe(to_exec.replace(s, f'# {s}'), global_vars, local_vars)
            except Exception as e:
                print(f'Error: {e}')
                import pdb ; pdb.set_trace()
        else:
            exec_safe(to_exec, global_vars, local_vars)

        self.execution_history += f'\n{to_log.strip()}'

        if self._config['maintain_session']:
            self._variable_vars.update(local_vars)

        if self._config['has_return']:
            if self._name == 'parse_query_obj':
                try:
                    # there may be multiple objects returned, but we also want them to be unevaluated functions so that we can access latest obs
                    return IterableDynamicObservation(local_vars[self._config['return_value_name']])
                except AssertionError:
                    return DynamicObservation(local_vars[self._config['return_value_name']])
            return local_vars[self._config['return_value_name']]


def merge_dicts(dicts):
    return {
        k : v 
        for d in dicts
        for k, v in d.items()
    }
    

def exec_safe(code_str, global_vars=None, local_vars=None):
    banned_phrases = ['import', '__']
    for phrase in banned_phrases:
        assert phrase not in code_str
  
    if global_vars is None:
        global_vars = {}
    if local_vars is None:
        local_vars = {}
    empty_fn = lambda *args, **kwargs: None
    custom_global_vars = merge_dicts([
        global_vars,
        {'exec': empty_fn, 'eval': empty_fn}
    ])
    try:
        print('code to execute:')
        print(code_str)
        print(custom_global_vars)
        print(local_vars)

        exec(code_str, custom_global_vars, local_vars)
    except Exception as e:
        print(f'Error executing code:\n{code_str}')
        raise e
