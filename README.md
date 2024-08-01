
<img src="https://github.com/user-attachments/assets/b30e2c38-dc19-49a5-973d-51e1dafe5c4d" width="100%" />

<br/>

Use the CLI to upload, manage, and query documents based on fine-tuned LLM models. It uses the smartloop API to manage projects and documents and gives you an easy way to quickly process contents and reason based on it.


## Requirements

- Python 3.11

## Installation

Install the CLI with the following command:

```
pip install -U smartloop-cli

```
Once installed, check that everything is setup correclty:

![image](https://github.com/user-attachments/assets/eb41df67-d71d-4042-85ee-f1f8b72c0137)


## Creating an Account

First create an account using the `curl` command below, in Linux / macOS / WSL 2.0 / Ubuntu:


```
curl --location --request PUT 'https://api.smartloop.ai/v1/users' \
--header 'Content-Type: application/json' \
--header 'Accept: application/json' \
--data '{
  "email": "<string>",
  "password": "<string>",
  "name": "<string>"
}'

```

You will receive an email with the `token` that is needed to login into the CLI.

## Setup

Login to the CLI in the follwoing way using the token recevied in email:

```
smartloop-cli login
```

This command will prompt you for your token, copy and pase the token that you have recevied in your email. Next step it to create a  project, you can do so with the following command:

```bash
smartloop-cli project create --name Lexic
```

## Upload Document

Once the project is created , upload documents from your folder or a specific file, in this case I am uploading the a document describing Microsoft online services form my local machine

```bash
smartloop-cli upload --path=~/document1.pdf
```

## Run It

Finally, once the document is uploaded and processed, run the CLI to query:

```bash
smartloop-cli run
```

This will bring up the prompt to query your information from your uploaded document

```
$ smartloop-cli run
Current project: Microsoft(microsoft-24-07-2024)
Enter message (Ctrl-C to exit): what the SLA for azure open ai
⠋
The SLA (Service Level Agreement) for Azure OpenAI is not explicitly mentioned in the provided text. However, it's possible that the SLA for Azure OpenAI might be similar to the one mentioned below:

"Uptime Percentage"

* Service Credit:
+ < 99.9%: 10%
+ < 99%: 25%
+ < 95%: 100%

Please note that this is not a direct quote from the provided text, but rather an inference based on the format and structure of the SLA mentioned for other Azure services (e.g., SAP HANA on Azure High Availability Pair). To confirm the actual SLA for Azure OpenAI, you should check the official Microsoft documentation or contact their support team.

Enter message (Ctrl-C to exit):
```


In order to switch a default project, use the following command:

```
smartloop-cli project select 
```

In order to set `temparature` of your conversation, which ranges from 0.0 to 1.0, use the following command:

```bash 
smartloop-cli project set --temp=0.3
```

`LLM temperature is a parameter that influences the language model's output, determining whether the output is more random and creative or more predictable.`

The higher value tends towards more creative answer

## Supported Documents types

* PDF
* DOCX
* TXT (soon)
* CSV (soon)


## Contributing

Contributions are welcome! Please create a pull request with your changes. 


## Contact

If you have any questions or suggestions, please feel free to reach out to hello@smartloop.ai


## References

* [Smartloop API Documentation](https://api.smartloop.ai/v1/redoc)



## License

This project is licensed under the terms of the MIT license.
