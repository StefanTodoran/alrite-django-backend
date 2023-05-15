import sys
import json
import copy

needsValueID = [
  "MultipleChoice",
  "TextInput",
  "Counter",
]

requiredProps = {
  "Paragraph": [
    "text"
  ],
  "MediaItem": [
    "fileName",
    # "label"
  ],
  "MultipleChoice": [
    "label",
    "valueID",
    "multiselect",
  ],
  "Choice": [
    "text",
    "value",
    # "link",
  ],
  "TextInput": [
    "label",
    "type",
    "valueID",
    # "units",
    # "defaultValue",
  ],
  "Button": [
    "text",
    # "hint",
    "link",
  ],
  "Counter": [
    "title",
    # "hint",
    "timeLimit",
    "valueID",
    "offerManualInput",
  ],

  "Comparison": [
    "type",
    "threshold",
    "targetValueID",
    "satisfiedLink",
  ],
  "Selection": [
    "type",
    "targetValueID",
    "satisfiedLink",
  ],
}

def missingErrorMessage(type: str, prop: str) -> str:
  if prop == "pageID" or prop == "valueID":
    return f"{type.capitalize()} is missing a unique identifier!"
  else:
    return f"{type.capitalize()} requires {prop} property!"

# Verifies that the given ID property is unique given a set
# of possible ID values. Beware: modifies the provided set!
def ensureUniqueID(type: str, original, validated, prop: str, IDs: set, required: bool):
  if prop in original:
    value = original[prop]
    if value in IDs:
      IDs.discard(value)
      return True
    else:
      validated[prop] = f"Duplicate {prop} detected!"
      return False
  elif required:
    validated[prop] = missingErrorMessage(type, prop)
    return False
  else:
    return True

# Verifies the the property on the given object is an actual
# identifier in use somewhere. Supports optional properties.
def isValidID(type: str, original, validated, prop: str, IDs: set, required: bool):
  if prop in original:
    value = original[prop]
    if value in IDs:
      return True
    else:
      validated[prop] = f"Provided {prop} is not used by any page/component."
      return False
  elif required:
    validated[prop] = missingErrorMessage(type, prop)
    return False
  else:
    return True

# =========================== #
# PAGE & COMPONENT VALIDATION #

def validatePageObj(originalPage, validatedPage, pageIDs: set, unusedPageIDs: set):
  valid = True

  valid = ensureUniqueID("page", originalPage, validatedPage, "pageID", unusedPageIDs, True) and valid
  valid = isValidID("page", originalPage, validatedPage, "defaultLink", pageIDs, True) and valid

  if originalPage["defaultLink"] == originalPage["pageID"]:
    validatedPage["defaultLink"] = "Page should not link to itself!"
    valid = False
  
  if "title" not in originalPage:
    validatedPage["title"] = missingErrorMessage("page", "title")
    valid = False
  
  if "content" not in originalPage:
    validatedPage["content"] = missingErrorMessage("page", "content")
    valid = False

  return valid

def validateComponentObj(originalPage, originalComponent, validatedComponent, valueIDs: set, unusedValueIDs: set):
  valid = True

  componentType = originalComponent["component"]
  valid = ensureUniqueID(componentType, originalComponent, validatedComponent, "valueID", unusedValueIDs, componentType in needsValueID) and valid

  if "link" in originalComponent and originalComponent["link"] == originalPage["pageID"]:
    validatedComponent["link"] = "Component should link to a different page!"
    valid = False

  # for prop in requiredProps[componentType]:
    # print(componentType, prop, prop in originalComponent)

  return valid

# Takes a workflow object and returns a tuple with two contents.
# The first is a set of all page IDs and the second a set of all
# value IDs. Also takes an optional artifact parameter, this is an
# object which stores validation errors. 
def getAllIdentifiers(workflow, artifact):
  pageIDs = set()
  valueIDs = set()
  
  for pageIndex in range(len(workflow["pages"])):
    page = workflow["pages"][pageIndex]

    if "pageID" in page:
      pageIDs.add(page["pageID"])
    else:
      artifact["pageID"] = missingErrorMessage("page", "pageID")
    
    for componentIndex in range(len(page["content"])):
      component = page["content"][componentIndex]

      if "valueID" in component:
        valueIDs.add(component["valueID"])
      elif component["component"] in needsValueID:
        workflow["content"][componentIndex]["valueID"] = missingErrorMessage("component", "valueID")
  
  return pageIDs, valueIDs

def deepCopyWorkflowStructure(workflow):
  artifact = {
    "pages": [],
  }
  
  for pageIndex in range(len(workflow["pages"])):
    originalPage = workflow["pages"][pageIndex]

    artifact["pages"].append({
      "pageID": originalPage["pageID"],
      "content": [],
    })
    validatedPage = artifact["pages"][pageIndex]

    for componentIndex in range(len(originalPage["content"])):
      originalComponent = originalPage["content"][componentIndex]

      validatedPage["content"].append({
        "component": originalComponent["component"]
      })

  return artifact

# Validates the given workflow, returning an json-style object where
# properties map to error messages. Does not mutate the input workflow.
def validateWorkflow(workflow):
  artifact = deepCopyWorkflowStructure(workflow)
  
  pageIDs, valueIDs = getAllIdentifiers(workflow, True)

  unusedPageIDs = copy.copy(pageIDs)
  unusedValueIDs = copy.copy(valueIDs)

  valid = True

  for pageIndex in range(len(workflow["pages"])):
    originalPage = workflow["pages"][pageIndex]
    validatedPage = artifact["pages"][pageIndex]

    valid = validatePageObj(originalPage, validatedPage, pageIDs, unusedPageIDs) and valid

    for componentIndex in range(len(originalPage["content"])):
      originalComponent = originalPage["content"][componentIndex]
      validatedComponent = validatedPage["content"][componentIndex]

      valid = validateComponentObj(originalPage, originalComponent, validatedComponent, valueIDs, unusedValueIDs) and valid

  return artifact, valid

# ============== #
# VALIDATION CLI #

def readWorkflowFromFile(path: str):
  with open(path, 'r') as file:
    workflow = json.load(file)

  print(f"Successfully loaded workflow '{workflow['name']}'\n")
  return workflow

if __name__ == "__main__":
  if (len(sys.argv) != 3):
    print(f"Wrong number of arguments, got {len(sys.argv) - 1}, expected 2")
    print("Usage: python validation.py {input file} {output file}")
    sys.exit()
  else:
    print(f"Reading workflow from '{sys.argv[1]}'")
    data = readWorkflowFromFile(sys.argv[1])
    artifact, valid = validateWorkflow(data)
    
    if valid: 
      print("Workflow valid!")
    else:
      print("Workflow invalid!")

    print(f"Writing validation artifact to '{sys.argv[2]}'")
    with open(sys.argv[2], 'w') as file:
      json.dump(artifact, file)