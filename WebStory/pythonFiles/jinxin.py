from pathlib import Path
import json
import requests
import io
import base64
from PIL import Image, PngImagePlugin
from requests.auth import HTTPBasicAuth
import openai
from flask import Flask, request, render_template,jsonify

#Text part

#generate a title for a web story
def generateTitle(relatedtopics):
    prompt = f"generate a title for an article. The article has 6 related subtopics '{relatedtopics}'"
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        temperature=0.5,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    result_dict = response.to_dict()
    title = result_dict["choices"][0]["text"]
    json_files = Path(__file__).parents[1] /"static"/"webstory_jinxin"/"json"
    with open(json_files/"title.json", "w") as f:
        json.dump(title, f)

# Remove not User-friendly elements for summeries
def split_into_sentences(input_string):
    lines = input_string.split("\n")
    lines = [line.strip() for line in lines if line.strip()]
    lines = [line.split(".", 1)[-1].strip() for line in lines]
    return lines

#Generate 6 sub-topics related to topic or text
def generate_related_topics(topic):
    prompt = f"Use your imagination and must generate 6 related topics to '{topic}'"
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        temperature=0.5,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    result_dict = response.to_dict()
    text = result_dict["choices"][0]["text"]
    generateTitle(text)
    return split_into_sentences(text)
# Generate all text related to 6 sections
def generate6sections(text):
    openai.api_key = "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"
    topics = generate_related_topics(text)
    num_summary_sentences = 10
    model_engine = "text-davinci-002"
    prompt = (
        "Write an article with 6 sections, each discussing a different topic. "
        "The first section should be about {0}. The second section should be about {1}. "
        "The third section should be about {2}. The fourth section should be about {3}. "
        "The fifth section should be about {4}. The sixth section should be about {5}. "
        "In each section, include {6} summary sentences."
    )
    temperature = 0.7
    max_tokens = 2048
    article_sections = []
    for i in range(len(topics)):
        section_heading = f"Section {i+1}: {topics[i]}"
        prompt_text = prompt.format(*topics, num_summary_sentences)
        prompt_text += f"\n\n{section_heading}\n\n"
        response = openai.Completion.create(
            engine=model_engine,
            prompt=prompt_text,
            temperature=temperature,
            max_tokens=max_tokens,
            n=1,
            stop=None,
            timeout=60,
        )
        section_content = response.choices[0].text.strip()
        for i in range(1, 11):
            section_content = section_content.replace(f"{i}.", "")
        summary_sentences = []
        prompt_text = f"Summarize the key points of {section_heading} in {num_summary_sentences} sentences."
        response = openai.Completion.create(
            engine=model_engine,
            prompt=prompt_text,
            temperature=temperature,
            max_tokens=max_tokens,
            n=1,
            stop=None,
            timeout=60,
        )
        summary_sentences = [s.strip() for s in response.choices[0].text.split("\n")]

        article_sections.append({
            "section_heading": section_heading,
            "section_content": section_content,
            "summary_sentences": summary_sentences
        })

    json_files = Path(__file__).parents[1] /"static"/"webstory_jinxin"/"json"
    with open(json_files/"article.json", "w") as f:
        json.dump(article_sections, f)    
# post sections to frontend
def postSections():
    json_files = Path(__file__).parents[1] /"static"/"webstory_jinxin"/"json"
    with open(json_files/'article.json') as fd:
        json_data = json.load(fd)
    return jsonify(result=json_data)
# post sections to frontend
def postTitle():
    json_files = Path(__file__).parents[1] /"static"/"webstory_jinxin"/"json"
    with open(json_files/'title.json') as fd:
        json_data = json.load(fd)
    return jsonify(result=json_data)


# images part
# call generateImages function to generate all images
def deliverImages():
    json_files = Path(__file__).parents[1] /"static"/"webstory_jinxin"/"json"
    with open(json_files/'article.json') as fd:
        json_data = json.load(fd)
        for i in range(6):
            generateImages(json_data[i]['section_content'], 3*i)

# generate imgs and save in a folder
def generateImages(text, start):
    #url = "http://129.187.105.32:7861"
    url = 'http://129.187.105.233:8000'
    username = "NLPPP23"
    password = "WDV&LDV"
    basic = HTTPBasicAuth(username, password)
    negative_prompt = ""
    prompt = text
    width = 512
    height = 768
    negative_prompt = "(deformed iris, deformed pupils, semi-realistic, cgi, 3d, render, sketch, cartoon, drawing, anime:1.4), text, close up, cropped, out of frame, worst quality, low quality, jpeg artifacts, ugly, duplicate, morbid, mutilated, extra fingers, mutated hands, poorly drawn hands, poorly drawn face, mutation, deformed, blurry, dehydrated, bad anatomy, bad proportions, extra limbs, cloned face, disfigured, gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs, fused fingers, too many fingers, long neck"
    payload = {
                "enable_hr": False,
                "denoising_strength": 0,
                "firstphase_width": 0,
                "firstphase_height": 0,
                "hr_scale": 2,
                "hr_upscaler": "string",
                "hr_second_pass_steps": 0,
                "hr_resize_x": 0,
                "hr_resize_y": 0,
                "prompt": prompt,
                "styles": [
                    "string"
                ],
                "seed": -1,
                "subseed": -1,
                "subseed_strength": 0,
                "seed_resize_from_h": -1,
                "seed_resize_from_w": -1,
                # "sampler_name": "Euler a",
                "batch_size": 3, # for generate 3 images for every section
                "n_iter": 1,
                "steps": 50,
                "cfg_scale": 7,
                "width": width,
                "height": height,
                "restore_faces": False,
                "tiling": False,
                "do_not_save_samples": False,
                "do_not_save_grid": False,
                "negative_prompt": negative_prompt,
                "eta": 0,
                "s_churn": 0,
                "s_tmax": 0,
                "s_tmin": 0,
                "s_noise": 1,
                "override_settings": {},
                "override_settings_restore_afterwards": True,
                "script_args": [],
                #"sampler_index": "DPM++ SDE Karras",
                "sampler_index": "Euler a",
                "script_name": "",
                "send_images": True,
                "save_images": False,
                "alwayson_scripts": {}
            }
    response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload, auth=basic)
    r = response.json()
    load_r = json.loads(r['info'])
    meta = load_r["infotexts"][0]
    imgs_files = Path(__file__).parents[1] /"static"/"webstory_jinxin"/"imgs"
    a = start
    for i in r['images']:
        image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))
        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", meta)        
        image.save(imgs_files/f'output_{a}.png', pnginfo=pnginfo)
        a = a + 1

