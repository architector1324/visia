#!/bin/bash
"exec" "/home/arch/AI/Projects/VisionAI/venv/bin/python" "$0" "$@"

import io
import PIL
import base64
import ollama
import argparse
import pyperclip
import subprocess
import pyperclipimg

DEFAULT_MODEL = 'gemma3'
DEFAULT_PATH = '/home/arch/AI/Projects/VisionAI/'

MODELS = [
    'gemma3',
    'gemma3:12b',
    'qwen2.5vl',
    'qwen2.5vl:3b'
]

def get_image(clip, area):
    try:
        if clip:
            image = pyperclipimg.paste()
            if not image:
                return None
        else:
            command = ['gnome-screenshot', '-a' if area else '-w', '-p', '-f', f'{DEFAULT_PATH}/.tmp.png']
            subprocess.run(command, check=True)

            image = PIL.Image.open(f'{DEFAULT_PATH}/.tmp.png')

        buffered = io.BytesIO()
        image.save(buffered, format='PNG')
        
        img_bytes = buffered.getvalue()
        img = base64.b64encode(img_bytes).decode('utf-8')

        # print(img)
        return img

    except Exception as e:
        print(f'Произошла ошибка: {e}')
        return None


def prompt_window():
    try:
        command = [
            'zenity',
            '--entry',
            '--title=Vision AI',
            '--text=Prompt'
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,  # Декодировать вывод в строку
            check=True  # Генерировать исключение, если zenity вернет ошибку
        )
        return result.stdout.strip()

    except Exception as e:
        print(f'Произошла ошибка: {e}')
        return None


def model_window():
    try:
        command = [
            'zenity',
            '--list',
            '--title=Vision AI',
            '--text=Choose model',
            '--column=Models',
        ]
        command.extend(MODELS)

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,  # Декодировать вывод в строку
            check=True  # Генерировать исключение, если zenity вернет ошибку
        )
        return result.stdout.strip()

    except Exception as e:
        print(f'Произошла ошибка: {e}')
        return None


def output_window(text):
    try:
        # copy to clipboard
        pyperclip.copy(text)

        # show window
        command = [
            'zenity',
            '--info',
            '--title=Vision AI',
            f'--text={text}'
        ]
        subprocess.run(command, check=True)
    except Exception as e:
        print(f'Произошла ошибка: {e}')
        return None


# main
if __name__ == '__main__':
    # parse arguments
    parser = argparse.ArgumentParser(description='Vision AI')
    parser.add_argument('-m', '--model', default=DEFAULT_MODEL, type=str, help='LLM model')
    parser.add_argument('-s', '--stream', action='store_true', default=False, help='Stream output')
    parser.add_argument('-a', '--address', default='0.0.0.0:11434', type=str, help='Server host address')
    parser.add_argument('-c', '--clip', action='store_true', help='Use clipboard instead screenshot')
    parser.add_argument('-w', '--win', action='store_true', help='Show prompt window')
    parser.add_argument('--area', action='store_true', help='Area screenshot')
    parser.add_argument('--choose', action='store_true', help='Show models window')
    parser.add_argument('-p', '--prompt', type=str, help='Prompt')

    args = parser.parse_args()

    # get image
    image = get_image(args.clip, args.area)
    if not image:
        print('Нет изображения.')
        exit(0)

    # generate
    model = model_window() if args.choose else args.model
    prompt = prompt_window() if args.win else args.prompt

    llm = ollama.Client(host=args.address)

    if not args.stream:
        answer = llm.generate(
            model=model,
            prompt=prompt,
            stream=args.stream,
            images=[image],
            keep_alive=0,
            # options={'num_ctx': 8192}
        )['response'].strip()
        print(answer)

        if args.win:
            output_window(answer)

    else:
        text_s = llm.generate(
            model=model,
            prompt=prompt,
            stream=args.stream,
            images=[image],
            keep_alive=0,
            # options={'num_ctx': 8192}
        )
        for t in text_s:
            print(t['response'], end='', flush=True)
    print()
