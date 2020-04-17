+++
title = "The Encryption Compendium"
description = "The encryption literature database"
type = "landing page"
draft = false
+++

{{< section
  class="bg-white uk-margin-top"
  section-header="About us"
  section-header-id="about" >}}

<p>
  {{< text-lead >}}
  Encryption provides security and ensures user privacy on the internet.
  {{< /text-lead >}}
  However, encryption can also complicate law enforcement's job, making it difficult to investigate cybercrimes or obtain intelligence on issues related to national security. This frames the encryption policy debate as being user privacy set against national security. Often these debates lack input from different resources, and they happen over and over again with the same debate points being applied to an evolving technological landscape.
</p>

<p>
  Our mission is to serve as central hub for policy makers, law practitioners, and the general public to understand the encryption debate. We have put together a comprehensive collection of research relating to the main themes of the encryption policy debate in the United States from 1970-2020.
</p>

{{< /section >}}

{{< section >}}
{{% text-lead %}}
**Search the encryption literature for the following categories:**
{{% /text-lead %}}

  <form id="tag_search_form" method="GET" action="{% url 'search' %}">
    <div class="uk-width-8-10@m uk-text-break">
      <div id="tag-buttons" class="uk-grid uk-grid-small" uk-grid="" data-uk-button-checkbox="">
      </div>

      {{< button
          class="uk-margin-left uk-margin-top uk-button-secondary"
          onclick="tag_search()"
          icon="arrow-right" >}}
        Go
      {{< /button >}}

    </div>
  </form>
{{< /section >}}

{{< section
  class="bg-white"
  section-header="Team"
  section-header-id="team" >}}

<div class="uk-flex uk-flex-center uk-child-width-1-2@m uk-margin-top uk-grid-large uk-text-middle" uk-grid>
{{% landing-page/team
  title="Silicon Flatirons Research Team"
  subtitle="Led by Amie Stepanovich, Silicon Flatirons Director" %}}
- [Shannon Brunston](https://www.linkedin.com/in/shannonbrunston/)
- Slate Herman
- Jordan Regenie
- Stacey Weber
{{% /landing-page/team %}}
{{% landing-page/team
  title="TCP Web Development Team"
  subtitle="Led by Dr. Dan Massey, TCP Program Director" %}}
- [Will Shand](https://kernelmethod.dev)
- Pranav Gummaraj Srinivas
{{% /landing-page/team %}}
</div>

{{< /section >}}
