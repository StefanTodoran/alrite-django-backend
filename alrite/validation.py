import sys
import json

needsValueID = [
  "MultipleChoice",
  "TextInput",
  "Counter",
]

def missingErrorMessage(type: str, prop: str) -> str:
  if prop == "pageID" or prop == "valueID":
    return f"{type.capitalize()} is missing a unique identifier!"
  else:
    return f"{type.capitalize()} requires {prop} property!"

# Verifies that the given property is unique given a list
# of possible values. Beware: modifies the provided list!
def ensureUniqueID(type: str, obj, prop: str, IDs: list):
  if prop in obj:
    value = obj[prop]
    if value in IDs:
      IDs.remove(value)
    else:
      obj[prop] = f"Duplicate {prop} detected!"
  else:
    obj[prop] = missingErrorMessage(type, prop)

# Verifies the the property on the given object is an actual
# identifier in use somewhere. Supports optional properties.
def isValidID(type: str, obj, prop: str, IDs: list, required: bool):
  if prop in obj:
    value = obj[prop]
    if value not in IDs:
      obj[prop] = f"Provided {prop} is not used by any page/component."
  elif required:
    obj[prop] = missingErrorMessage(type, prop)

def validatePageObj(page, pageIDs, unusedPageIDs):
  ensureUniqueID("page", page, "pageID", unusedPageIDs)

  isValidID("page", page, "defaultLink", pageIDs, True)
  if page["defaultLink"] == page["pageID"]:
    page["defaultLink"] = "Page should not link to itself!"
  
  if "title" not in page:
    page["title"] = missingErrorMessage("page", "title")
  
  if "content" not in page:
    page["content"] = missingErrorMessage("page", "content")

# Takes a workflow object and returns a tuple with two contents.
# The first is a list of all page IDs and the second a list of all
# value IDs. Also takes a boolean doValidation, signaling whether to
# modify the workflow object with errors if identifiers are missing.
def getAllIdentifiers(workflow, doValidation):
  pageIDs = []
  valueIDs = []
  
  for pageIndex in range(len(workflow["pages"])):
    page = workflow["pages"][pageIndex]

    if "pageID" in page:
      pageIDs.append(page["pageID"])
    else:
      page["pageID"] = missingErrorMessage("page", "pageID")
    
    for componentIndex in range(len(page["content"])):
      component = page["content"][componentIndex]

      if "valueID" in component:
        valueIDs.append(component["valueID"])
      elif component["component"] in needsValueID:
        component["valueID"] = missingErrorMessage("component", "valueID")
  
  return pageIDs, valueIDs

def readWorkflowFromFile(path: str):
  with open(path, 'r') as file:
    workflow = json.load(file)

  print(f"Successfully loaded workflow '{workflow['name']}'\n")
  return workflow

def validateWorkflow(workflow):
  pageIDs, valueIDs = getAllIdentifiers(workflow, True)

  unusedPageIDs = list(pageIDs)
  unusedValueIDs = list(valueIDs)

  for index in range(len(workflow["pages"])):
    page = workflow["pages"][index]

    validatePageObj(page, pageIDs, unusedPageIDs)

  return workflow

if __name__ == "__main__":
  if (len(sys.argv) != 3):
    print(f"Wrong number of arguments, got {len(sys.argv) - 1}, expected 2")
    print("Usage: python validation.py {input file} {output file}")
    sys.exit()
  else:
    print(f"Reading workflow from '{sys.argv[1]}'")
    artifact = readWorkflowFromFile(sys.argv[1])
    
    print(f"Writing validation artifact to '{sys.argv[2]}'")
    with open(sys.argv[2], 'w') as file:
      json.dump(artifact, file)