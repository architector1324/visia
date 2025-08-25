import io
import PIL
import base64
import ollama
import argparse
import pyperclip
import subprocess
import pyperclipimg

DEFAULT_MODEL = 'gemma3'
SCREENSHOT_PATH = '/tmp/visia.png'

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
            command = ['gnome-screenshot', '-a' if area else '-w', '-p', '-f', SCREENSHOT_PATH]
            subprocess.run(command, check=True)

            image = PIL.Image.open(SCREENSHOT_PATH)

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
            '--title=VisIA',
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
            '--title=VisIA',
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
            '--title=VisIA',
            f'--text={text}'
        ]
        subprocess.run(command, check=True)
    except Exception as e:
        print(f'Произошла ошибка: {e}')
        return None


# main
if __name__ == '__main__':
    # parse arguments
    parser = argparse.ArgumentParser(description='VisIA')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # cli
    cli_parser = subparsers.add_parser('cli', help='CLI mode')
    cli_parser.add_argument('-m', '--model', default=DEFAULT_MODEL, type=str, help='LLM model')
    cli_parser.add_argument('-s', '--stream', action='store_true', default=False, help='Stream output')
    cli_parser.add_argument('-a', '--address', default='0.0.0.0:11434', type=str, help='Server host address')
    cli_parser.add_argument('-c', '--clip', action='store_true', help='Use clipboard instead screenshot')
    cli_parser.add_argument('--area', action='store_true', help='Area screenshot')
    cli_parser.add_argument('prompt', nargs='+', type=str, help='Prompt for model')

    # gui
    gui_parser = subparsers.add_parser('gui', help='GUI mode')
    gui_parser.add_argument('-a', '--address', default='0.0.0.0:11434', type=str, help='Server host address')
    gui_parser.add_argument('-c', '--clip', action='store_true', help='Use clipboard instead screenshot')
    gui_parser.add_argument('--area', action='store_true', help='Area screenshot')
    gui_parser.add_argument('--choose', action='store_true', help='Show models window')

    args = parser.parse_args()

    # get image
    image = get_image(args.clip, args.area)
    if not image:
        print('Нет изображения.')
        exit(0)

    # get prompt and model
    if args.command == 'cli':
        model = args.model
        prompt = ' '.join(args.prompt).strip()
        stream = args.stream
    elif args.command == 'gui':
        model = model_window() if args.choose else DEFAULT_MODEL
        prompt = prompt_window()
        stream = False
    else:
        parser.print_help()
        exit()

    # generate
    llm = ollama.Client(host=args.address)

    if not stream:
        answer = llm.generate(
            model=model,
            prompt=prompt,
            stream=stream,
            images=[image],
            keep_alive=0,
            # options={'num_ctx': 8192}
        )['response'].strip()
        print(answer)

        if args.command == 'gui':
            output_window(answer)

    else:
        text_s = llm.generate(
            model=model,
            prompt=prompt,
            stream=stream,
            images=[image],
            keep_alive=0,
            # options={'num_ctx': 8192}
        )
        for t in text_s:
            print(t['response'], end='', flush=True)
    print()
