import yaml


with open('profiles.yml') as fp:
    profiles = yaml.safe_load(fp)

for profile_id, profile in profiles.items():
    profile['id'] = profile_id
