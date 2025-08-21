import * as RecitationsType from "../types/recitations";
import { AxiosResponse } from "axios";
import { Connection } from "../client/connection";
import { BaseController } from "../utils/baseController";
import { RequestConfig } from "../utils/globalTypes";

export class RecitationsController extends BaseController {

    constructor(connection: Connection, token?: string) {
        super(connection, token);
    }
    
    /** GET /recitations/ */
    async list(config?: RequestConfig<RecitationsType.RecitationsListRequestParams>
    ): Promise<AxiosResponse<RecitationsType.RecitationsListResponseData>> {
        return await this.axiosGet(`/recitations/`, config);
    }
    
    /** POST /recitations/ */
    async create(data: RecitationsType.RecitationsCreateRequestData,config?: RequestConfig
    ): Promise<AxiosResponse<RecitationsType.RecitationsCreateResponseData>> {
        return await this.axiosPost(`/recitations/`, data, config);
    }
    
    /** GET /recitations/{uuid}/ */
    async retrieve(uuid: string,config?: RequestConfig
    ): Promise<AxiosResponse<RecitationsType.RecitationsRetrieveResponseData>> {
        return await this.axiosGet(`/recitations/${uuid}/`, config);
    }
    
    /** PUT /recitations/{uuid}/ */
    async update(uuid: string,data: RecitationsType.RecitationsUpdateRequestData,config?: RequestConfig
    ): Promise<AxiosResponse<RecitationsType.RecitationsUpdateResponseData>> {
        return await this.axiosPut(`/recitations/${uuid}/`, data, config);
    }
    
    /** PATCH /recitations/{uuid}/ */
    async partialUpdate(uuid: string,data: RecitationsType.RecitationsPartialupdateRequestData,config?: RequestConfig
    ): Promise<AxiosResponse<RecitationsType.RecitationsPartialupdateResponseData>> {
        return await this.axiosPatch(`/recitations/${uuid}/`, data, config);
    }
    
    /** DELETE /recitations/{uuid}/ */
    async delete(uuid: string,config?: RequestConfig
    ): Promise<AxiosResponse<any>> {
        return await this.axiosDelete(`/recitations/${uuid}/`, config);
    }
    
}